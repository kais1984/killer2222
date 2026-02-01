"""
Sales signals: Auto-create accounting entries when sales/payments occur
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal
from sales.models import Sale, SaleLine, Invoice, Payment
from financeaccounting.models import JournalEntry, JournalEntryLine, Account
from inventory.models import StockMovement
from django.utils import timezone


@receiver(post_save, sender=Sale)
def create_sale_accounting_entry(sender, instance, created, **kwargs):
    """
    When a sale is created, auto-create journal entry:
    DR Accounts Receivable
    CR Sales Revenue
    """
    if not created or not instance.customer:
        return
    
    try:
        # Skip if already has journal entries
        if JournalEntry.objects.filter(sale_id=str(instance.id)).exists():
            return
        
        with transaction.atomic():
            # Get or create accounts
            ar_account, _ = Account.objects.get_or_create(
                account_code='1200',
                defaults={
                    'account_name': 'Accounts Receivable',
                    'account_type': 'asset',
                    'account_subtype': 'accounts_receivable',
                }
            )
            
            sales_account, _ = Account.objects.get_or_create(
                account_code='4100',
                defaults={
                    'account_name': 'Sales Revenue',
                    'account_type': 'revenue',
                    'account_subtype': 'sales',
                }
            )
            
            # Create journal entry
            je = JournalEntry.objects.create(
                entry_type='sale',
                entry_date=instance.sale_date.date(),
                description=f'Sale {instance.sale_number}',
                sale_id=instance.id,
                created_by=instance.created_by,
            )
            
            # Create debit line (AR)
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=ar_account,
                line_type='debit',
                amount=instance.total_amount,
                description=f'AR for sale {instance.sale_number}'
            )
            
            # Create credit line (Sales Revenue)
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=sales_account,
                line_type='credit',
                amount=instance.total_amount,
                description=f'Revenue from sale {instance.sale_number}'
            )
    except Exception as e:
        # Log error but don't fail the save
        print(f"Error creating sale accounting entry: {e}")


@receiver(post_save, sender=SaleLine)
def create_stock_movement_on_sale(sender, instance, created, **kwargs):
    """
    When a sale line is created, record stock movement and COGS entry
    """
    if not created or not instance.product or not instance.sale:
        return
    
    try:
        with transaction.atomic():
            # Record stock movement
            current_stock = instance.product.quantity_in_stock
            new_stock = current_stock - instance.quantity
            
            StockMovement.objects.create(
                product=instance.product,
                movement_type='sale',
                quantity_change=-instance.quantity,
                quantity_before=current_stock,
                quantity_after=new_stock,
                sale_id=instance.sale.id,
                reference=instance.sale.sale_number,
                recorded_by=instance.sale.created_by,
                notes=f'Sale line for {instance.sale.sale_number}'
            )
            
            # Update product stock
            instance.product.quantity_in_stock = new_stock
            instance.product.save()
            
            # Create COGS journal entry
            cogs_account, _ = Account.objects.get_or_create(
                account_code='5100',
                defaults={
                    'account_name': 'Cost of Goods Sold',
                    'account_type': 'expense',
                    'account_subtype': 'cogs',
                }
            )
            
            inventory_account, _ = Account.objects.get_or_create(
                account_code='1300',
                defaults={
                    'account_name': 'Inventory',
                    'account_type': 'asset',
                    'account_subtype': 'inventory',
                }
            )
            
            # Calculate cost (assuming product cost field exists)
            cost_amount = getattr(instance.product, 'cost_price', instance.unit_price) * instance.quantity
            
            je = JournalEntry.objects.create(
                entry_type='stock_movement',
                entry_date=instance.sale.sale_date.date(),
                description=f'COGS for {instance.product.name} (Sale {instance.sale.sale_number})',
                sale_id=instance.sale.id,
                created_by=instance.sale.created_by,
            )
            
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=cogs_account,
                line_type='debit',
                amount=cost_amount,
                description=f'COGS: {instance.product.name} x {instance.quantity}'
            )
            
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=inventory_account,
                line_type='credit',
                amount=cost_amount,
                description=f'Inventory reduction: {instance.product.name}'
            )
    except Exception as e:
        print(f"Error creating stock movement: {e}")


@receiver(post_save, sender=Payment)
def create_payment_accounting_entry(sender, instance, created, **kwargs):
    """
    When a payment is received, auto-create journal entry:
    DR Cash/Bank
    CR Accounts Receivable
    """
    if not created or not instance.sale:
        return
    
    try:
        with transaction.atomic():
            # Get or create accounts
            cash_account, _ = Account.objects.get_or_create(
                account_code='1100',
                defaults={
                    'account_name': 'Cash',
                    'account_type': 'asset',
                    'account_subtype': 'cash',
                }
            )
            
            ar_account, _ = Account.objects.get_or_create(
                account_code='1200',
                defaults={
                    'account_name': 'Accounts Receivable',
                    'account_type': 'asset',
                    'account_subtype': 'accounts_receivable',
                }
            )
            
            # Create journal entry
            je = JournalEntry.objects.create(
                entry_type='payment',
                entry_date=instance.payment_date,
                description=f'Payment received for {instance.sale.sale_number} ({instance.payment_method})',
                payment_id=instance.id,
                sale_id=instance.sale.id,
                created_by=instance.created_by,
            )
            
            # Create debit line (Cash)
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=cash_account,
                line_type='debit',
                amount=instance.amount,
                description=f'Payment received: {instance.payment_method}'
            )
            
            # Create credit line (AR reduction)
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=ar_account,
                line_type='credit',
                amount=instance.amount,
                description=f'AR reduction for sale {instance.sale.sale_number}'
            )
    except Exception as e:
        print(f"Error creating payment accounting entry: {e}")


@receiver(post_save, sender=Payment)
def handle_payment_reversal(sender, instance, created, **kwargs):
    """
    If a payment is marked as reversed, create reversing journal entries
    """
    if created or not instance.reversed_by:
        return
    
    try:
        with transaction.atomic():
            # Find original journal entry
            original_je = JournalEntry.objects.filter(payment_id=instance.id).first()
            if not original_je:
                return
            
            # Create reversing entry
            reversing_je = JournalEntry.objects.create(
                entry_type='payment_reversal',
                entry_date=timezone.now().date(),
                description=f'Reversal of payment {instance.payment_number}',
                payment_id=instance.id,
                sale_id=instance.sale.id,
                created_by=instance.created_by,
                reversed_by=original_je,  # Link to original
            )
            
            # Copy lines in reverse (credit becomes debit, debit becomes credit)
            for line in original_je.lines.all():
                reverse_type = 'credit' if line.line_type == 'debit' else 'debit'
                JournalEntryLine.objects.create(
                    journal_entry=reversing_je,
                    account=line.account,
                    line_type=reverse_type,
                    amount=line.amount,
                    description=f'Reversal: {line.description}'
                )
    except Exception as e:
        print(f"Error creating reversal entry: {e}")
