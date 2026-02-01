"""
Accounting Entry Generation Service

Automatically creates journal entries for:
1. Sale invoicing (revenue recognition)
2. Payment received (cash/AR reduction)
3. Stock movement (COGS & inventory reduction)
4. Payment reversal (offset entries)

This ensures ALL financial transactions are double-entry and auditable.
No manual journal entries for standard transactions.
"""

from django.db import transaction, IntegrityError
from django.utils import timezone
from decimal import Decimal
import uuid
from financeaccounting.models import JournalEntry, Account
from sales.models import Sale, Invoice, Payment, SaleLine
from accounting.models import Expense


class AccountingEntryError(Exception):
    """Raised when accounting entry creation fails"""
    pass


class SaleAccountingService:
    """
    Manages accounting entries for sales lifecycle:
    Sale → Invoice → Payment → Inventory
    """
    
    # GL Account codes (configure in Django admin)
    ACCOUNT_CODES = {
        'accounts_receivable': '1200',  # Asset
        'sales_revenue': '4100',        # Revenue
        'sales_tax_payable': '2200',    # Liability
        'inventory': '1100',            # Asset
        'cogs': '5100',                 # Expense
        'cash': '1000',                 # Asset
        'undeposited_funds': '1050',    # Asset (for pending deposits)
    }
    
    @staticmethod
    def get_account(account_code):
        """Get account by code, raise error if not found"""
        try:
            return Account.objects.get(account_code=account_code, is_active=True)
        except Account.DoesNotExist:
            raise AccountingEntryError(
                f"Required GL account not configured: {account_code}"
            )
    
    @staticmethod
    @transaction.atomic
    def post_invoice(invoice: Invoice):
        """
        Post invoice to GL when created from sale.
        
        Creates journal entry:
        Debit: Accounts Receivable (total invoice amount)
        Credit: Sales Revenue (sale amount)
        Credit: Sales Tax Payable (tax amount)
        
        This is the REVENUE RECOGNITION entry.
        """
        if not invoice.sale:
            raise AccountingEntryError("Invoice must be linked to a sale")
        
        try:
            ar_account = SaleAccountingService.get_account('accounts_receivable')
            revenue_account = SaleAccountingService.get_account('sales_revenue')
            tax_account = SaleAccountingService.get_account('sales_tax_payable')
            
            # Create journal entry
            entry = JournalEntry.objects.create(
                journal_number=SaleAccountingService._generate_journal_number(),
                entry_type='sale',
                entry_date=invoice.invoice_date,
                description=f"Invoice {invoice.invoice_number} - Sale {invoice.sale.sale_number}",
                sale_id=invoice.sale.id
            )
            
            # Debit: Accounts Receivable
            entry.lines.create(
                account=ar_account,
                line_type='debit',
                amount=invoice.total_amount
            )
            
            # Credit: Sales Revenue
            entry.lines.create(
                account=revenue_account,
                line_type='credit',
                amount=invoice.subtotal
            )
            
            # Credit: Sales Tax Payable (if tax > 0)
            if invoice.tax_amount > 0:
                entry.lines.create(
                    account=tax_account,
                    line_type='credit',
                    amount=invoice.tax_amount
                )
            
            # Verify entry is balanced
            if not entry.is_balanced():
                raise AccountingEntryError("Journal entry not balanced")
            
            entry.status = 'posted'
            entry.save()
            
            return entry
            
        except Account.DoesNotExist as e:
            raise AccountingEntryError(f"Account not found: {str(e)}")
        except IntegrityError as e:
            raise AccountingEntryError(f"Database error: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def post_payment(payment: Payment):
        """
        Post payment to GL when received.
        
        Creates journal entry:
        Debit: Cash/Bank Account (payment amount)
        Credit: Accounts Receivable (invoice amount)
        
        This REDUCES AR and INCREASES CASH.
        """
        if not payment.sale:
            raise AccountingEntryError("Payment must be linked to a sale")
        
        try:
            ar_account = SaleAccountingService.get_account('accounts_receivable')
            cash_account = SaleAccountingService._get_payment_method_account(
                payment.payment_method
            )
            
            # Create journal entry
            entry = JournalEntry.objects.create(
                journal_number=SaleAccountingService._generate_journal_number(),
                entry_type='payment',
                entry_date=payment.payment_date,
                description=f"Payment {payment.payment_number} - {payment.payment_method} "
                           f"for Sale {payment.sale.sale_number}",
                payment_id=payment.id
            )
            
            # Debit: Cash/Bank Account
            entry.lines.create(
                account=cash_account,
                line_type='debit',
                amount=payment.amount
            )
            
            # Credit: Accounts Receivable
            entry.lines.create(
                account=ar_account,
                line_type='credit',
                amount=payment.amount
            )
            
            if not entry.is_balanced():
                raise AccountingEntryError("Journal entry not balanced")
            
            entry.status = 'posted'
            entry.save()
            
            return entry
            
        except Account.DoesNotExist as e:
            raise AccountingEntryError(f"Account not found: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def reverse_payment(payment: Payment, reversal_payment: 'Payment'):
        """
        Create reversal entry when payment is reversed (e.g., refund).
        
        Creates offset journal entry with opposite debits/credits.
        Original entry remains immutable.
        """
        try:
            ar_account = SaleAccountingService.get_account('accounts_receivable')
            cash_account = SaleAccountingService._get_payment_method_account(
                payment.payment_method
            )
            
            # Create reversal journal entry
            entry = JournalEntry.objects.create(
                journal_number=SaleAccountingService._generate_journal_number(),
                entry_type='payment_reversal',
                entry_date=timezone.now().date(),
                description=f"Reversal of Payment {payment.payment_number}",
                payment_id=reversal_payment.id
            )
            
            # Reverse debits/credits
            # Credit: Cash/Bank (reverse the debit)
            entry.lines.create(
                account=cash_account,
                line_type='credit',
                amount=payment.amount
            )
            
            # Debit: Accounts Receivable (reverse the credit)
            entry.lines.create(
                account=ar_account,
                line_type='debit',
                amount=payment.amount
            )
            
            if not entry.is_balanced():
                raise AccountingEntryError("Reversal entry not balanced")
            
            entry.status = 'posted'
            entry.save()
            
            return entry
            
        except Account.DoesNotExist as e:
            raise AccountingEntryError(f"Account not found: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def post_stock_movement(sale_line: SaleLine):
        """
        Post COGS and inventory reduction when invoice is created.
        
        Creates journal entry:
        Debit: Cost of Goods Sold (COGS)
        Credit: Inventory (asset reduction)
        
        This REDUCES inventory and RECOGNIZES COGS.
        
        Calculation:
        COGS = (product.cost_per_unit * quantity)
        """
        try:
            inventory_account = SaleAccountingService.get_account('inventory')
            cogs_account = SaleAccountingService.get_account('cogs')
            
            # Calculate COGS (cost per unit * quantity sold)
            product = sale_line.product
            cost_per_unit = product.cost_price  # Use cost_price from Product model
            cogs_amount = cost_per_unit * sale_line.quantity
            
            # Create journal entry
            entry = JournalEntry.objects.create(
                journal_number=SaleAccountingService._generate_journal_number(),
                entry_type='stock_movement',
                entry_date=sale_line.sale.sale_date.date() if hasattr(sale_line.sale.sale_date, 'date') else sale_line.sale.sale_date,
                description=f"COGS for {product.name} x {sale_line.quantity} "
                           f"(Invoice {sale_line.sale.invoice_set.first().invoice_number if sale_line.sale.invoice_set.exists() else 'pending'})",
                sale_id=sale_line.sale.id
            )
            
            # Debit: COGS
            entry.lines.create(
                account=cogs_account,
                line_type='debit',
                amount=cogs_amount
            )
            
            # Credit: Inventory
            entry.lines.create(
                account=inventory_account,
                line_type='credit',
                amount=cogs_amount
            )
            
            if not entry.is_balanced():
                raise AccountingEntryError("Stock movement entry not balanced")
            
            entry.status = 'posted'
            entry.save()
            
            return entry
            
        except Account.DoesNotExist as e:
            raise AccountingEntryError(f"Account not found: {str(e)}")
    
    @staticmethod
    def _get_payment_method_account(payment_method: str) -> Account:
        """Map payment method to GL account"""
        method_to_account = {
            'cash': '1000',              # Cash
            'card': '1000',              # Credit card (treat as cash for now)
            'transfer': '1000',          # Bank transfer
            'cheque': '1050',            # Undeposited funds (pending)
            'other': '1050',             # Undeposited funds
        }
        
        account_code = method_to_account.get(payment_method, '1000')
        return SaleAccountingService.get_account(account_code)
    
    @staticmethod
    def _generate_journal_number() -> str:
        """Generate unique journal entry number"""
        timestamp = timezone.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"JE-{timestamp}-{unique_id}"


class ExpenseAccountingService:
    """
    Manages accounting entries for expenses.
    """
    
    @staticmethod
    @transaction.atomic
    def post_expense(expense: Expense):
        """
        Post expense to GL.
        
        Creates journal entry:
        Debit: Expense Category GL Account
        Credit: Payment Method Account (cash, bank, or AP)
        """
        try:
            if not expense.gl_account:
                raise AccountingEntryError("Expense must have GL account mapped")
            
            expense_account = expense.gl_account
            payment_account = ExpenseAccountingService._get_payment_account(
                expense.payment_method
            )
            
            # Create journal entry
            entry = JournalEntry.objects.create(
                journal_number=SaleAccountingService._generate_journal_number(),
                entry_type='expense',
                entry_date=expense.expense_date,
                description=f"Expense: {expense.description} ({expense.get_expense_type_display()})",
                expense_id=expense.id
            )
            
            # Debit: Expense Account
            entry.lines.create(
                account=expense_account,
                line_type='debit',
                amount=expense.amount
            )
            
            # Credit: Payment Account (cash, bank, or AP)
            entry.lines.create(
                account=payment_account,
                line_type='credit',
                amount=expense.amount
            )
            
            if not entry.is_balanced():
                raise AccountingEntryError("Expense entry not balanced")
            
            entry.status = 'posted'
            entry.save()
            expense.status = 'posted'
            expense.save()
            
            return entry
            
        except Account.DoesNotExist as e:
            raise AccountingEntryError(f"Account not found: {str(e)}")
    
    @staticmethod
    def _get_payment_account(payment_method: str) -> Account:
        """Map expense payment method to GL account"""
        method_to_account = {
            'cash': '1000',                  # Cash
            'bank': '1000',                  # Bank
            'payable': '2100',               # Accounts Payable
            'credit_card': '1000',           # Credit card
        }
        
        account_code = method_to_account.get(payment_method, '1000')
        return SaleAccountingService.get_account(account_code)


class ExpenseAccountingService:
    """
    Manages accounting entries for expenses (Phase 3).
    
    Expenses are different from revenue:
    - Revenue is recognized when invoice is created
    - Expenses are recognized when approved and posted
    
    Journal entry:
    Debit: Expense Account (supplies, labor, utilities, etc.)
    Credit: Cash/Accounts Payable
    """
    
    ACCOUNT_CODES = {
        'cash': '1000',
        'accounts_payable': '2100',
        'supplies': '5200',
        'labor': '5300',
        'utilities': '5400',
        'rent': '5500',
        'marketing': '5600',
        'transportation': '5700',
        'maintenance': '5800',
        'salaries': '5900',
    }
    
    @staticmethod
    def get_account(account_code):
        """Get account by code, raise error if not found"""
        try:
            return Account.objects.get(account_code=account_code, is_active=True)
        except Account.DoesNotExist:
            raise AccountingEntryError(
                f"Required GL account not configured: {account_code}"
            )
    
    @staticmethod
    @transaction.atomic
    def post_expense(expense, user=None):
        """
        Post expense to GL when approved.
        
        Creates journal entry:
        Debit: Expense Account (from expense.account)
        Credit: Cash/Accounts Payable (1000 or 2100)
        
        This records the expense in the P&L.
        """
        from accounting.models import Expense
        
        if not isinstance(expense, Expense):
            raise AccountingEntryError("Invalid expense object")
        
        if not expense.account:
            raise AccountingEntryError("Expense must have an account assigned")
        
        try:
            # Get accounts
            expense_account = expense.account  # Already set and must be expense type
            if expense_account.account_type != 'expense':
                raise AccountingEntryError(f"Account {expense_account.account_code} is not an expense account")
            
            # Credit cash (assuming paid in cash; could be Accounts Payable if on credit)
            cash_account = ExpenseAccountingService.get_account('1000')
            
            # Create journal entry
            from financeaccounting.models import JournalEntry
            entry = JournalEntry.objects.create(
                journal_number=f"EXP-{expense.expense_number}",
                entry_type='expense',
                entry_date=expense.expense_date,
                description=f"Expense {expense.expense_number} - {expense.description}",
                expense_id=expense.id if hasattr(expense, 'id') else None
            )
            
            # Debit: Expense Account
            entry.lines.create(
                account=expense_account,
                line_type='debit',
                amount=expense.amount
            )
            
            # Credit: Cash
            entry.lines.create(
                account=cash_account,
                line_type='credit',
                amount=expense.amount
            )
            
            # Mark as posted
            entry.status = 'posted'
            entry.approved_by = user.username if user else 'System'
            entry.approved_at = timezone.now()
            entry.save()
            
            return entry
            
        except Exception as e:
            raise AccountingEntryError(f"Failed to post expense to GL: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def reverse_expense(expense, reason="Reversal"):
        """
        Reverse a posted expense entry (for corrections/cancellations).
        Creates offsetting journal entry.
        """
        from accounting.models import Expense
        from financeaccounting.models import JournalEntry
        
        if not expense.is_posted:
            raise AccountingEntryError("Cannot reverse an expense that hasn't been posted")
        
        try:
            # Get accounts
            expense_account = expense.account
            cash_account = ExpenseAccountingService.get_account('1000')
            
            # Create reversal entry (opposite debits/credits)
            entry = JournalEntry.objects.create(
                journal_number=f"REV-{expense.expense_number}",
                entry_type='expense_reversal',
                entry_date=timezone.now().date(),
                description=f"Reversal of Expense {expense.expense_number} - {reason}",
                expense_id=expense.id if hasattr(expense, 'id') else None
            )
            
            # Credit: Expense Account (opposite of original debit)
            entry.lines.create(
                account=expense_account,
                line_type='credit',
                amount=expense.amount
            )
            
            # Debit: Cash (opposite of original credit)
            entry.lines.create(
                account=cash_account,
                line_type='debit',
                amount=expense.amount
            )
            
            entry.status = 'posted'
            entry.save()
            
            # Mark original as reversed
            expense.is_posted = False
            expense.status = 'draft'
            expense.save()
            
            return entry
            
        except Exception as e:
            raise AccountingEntryError(f"Failed to reverse expense: {str(e)}")


class GLIntegrityService:
    """
    REFINEMENT 4: Verify GL always balanced
    
    Performs daily GL reconciliation and integrity checks:
    - Verifies all journal entries balance (debits = credits)
    - Identifies any unbalanced entries
    - Records integrity check history for audit trail
    - Prevents posting of unbalanced entries
    """
    
    @staticmethod
    def verify_balance():
        """
        Check if all journal entries balance
        Returns:
            dict: {'is_balanced': bool, 'total_debits': Decimal, 'total_credits': Decimal, 'issues': list}
        """
        from accounting.models import JournalEntry, JournalEntryLine
        
        entries = JournalEntry.objects.all()
        issues = []
        
        for entry in entries:
            lines = JournalEntryLine.objects.filter(journal_entry=entry)
            debits = sum(line.debit_amount for line in lines if line.debit_amount)
            credits = sum(line.credit_amount for line in lines if line.credit_amount)
            
            if debits != credits:
                issues.append({
                    'entry_id': entry.id,
                    'entry_number': entry.entry_number if hasattr(entry, 'entry_number') else str(entry.id),
                    'reference': entry.reference if hasattr(entry, 'reference') else 'N/A',
                    'debits': debits,
                    'credits': credits,
                    'discrepancy': debits - credits,
                    'entry_date': entry.entry_date if hasattr(entry, 'entry_date') else None,
                })
        
        return {
            'is_balanced': len(issues) == 0,
            'issues': issues,
            'issue_count': len(issues),
        }
    
    @staticmethod
    def daily_reconciliation(user):
        """
        Run daily GL reconciliation
        
        Args:
            user: User performing the reconciliation
            
        Returns:
            GLIntegrityCheck: The reconciliation record created
        """
        from accounting.models import JournalEntry, JournalEntryLine, GLIntegrityCheck
        
        # Get all posted entries
        entries = JournalEntry.objects.filter(status='posted') if hasattr(JournalEntry, 'status') else JournalEntry.objects.all()
        lines = JournalEntryLine.objects.filter(journal_entry__in=entries)
        
        # Calculate totals
        total_debits = sum(line.debit_amount for line in lines if line.debit_amount)
        total_credits = sum(line.credit_amount for line in lines if line.credit_amount)
        
        # Check balance (allow 0.01 for rounding)
        discrepancy = total_debits - total_credits
        is_balanced = abs(discrepancy) < Decimal('0.01')
        
        # Find unbalanced entries
        balance_check = GLIntegrityService.verify_balance()
        issues_count = balance_check['issue_count']
        
        # Create reconciliation record
        check = GLIntegrityCheck(
            total_debits=total_debits,
            total_credits=total_credits,
            is_balanced=is_balanced,
            discrepancy=discrepancy,
            issues_found=issues_count,
            performed_by=user,
            notes=f"Daily reconciliation: {len(lines)} lines, {issues_count} unbalanced entries"
        )
        check.save()
        
        return check
    
    @staticmethod
    def validate_entry_balance(journal_entry):
        """
        Validate a single journal entry balances before posting
        
        Args:
            journal_entry: JournalEntry to validate
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        from accounting.models import JournalEntryLine
        
        lines = JournalEntryLine.objects.filter(journal_entry=journal_entry)
        debits = sum(line.debit_amount for line in lines if line.debit_amount)
        credits = sum(line.credit_amount for line in lines if line.credit_amount)
        
        if debits != credits:
            return False, f"Entry does not balance: Debits ${debits} != Credits ${credits}"
        
        if debits == 0 and credits == 0:
            return False, "Entry has no amounts"
        
        return True, "Entry balances correctly"
    
    @staticmethod
    def get_reconciliation_summary(days=30):
        """
        Get GL reconciliation summary for past N days
        
        Args:
            days: Number of days to summarize
            
        Returns:
            dict: Summary statistics
        """
        from datetime import timedelta
        from accounting.models import GLIntegrityCheck
        
        cutoff_date = timezone.now().date() - timedelta(days=days)
        checks = GLIntegrityCheck.objects.filter(check_date__gte=cutoff_date)
        
        total_checks = checks.count()
        balanced_checks = checks.filter(is_balanced=True).count()
        unbalanced_checks = total_checks - balanced_checks
        
        return {
            'period_days': days,
            'total_checks': total_checks,
            'balanced_checks': balanced_checks,
            'unbalanced_checks': unbalanced_checks,
            'balance_success_rate': (balanced_checks / total_checks * 100) if total_checks > 0 else 0,
            'total_discrepancies': sum(check.discrepancy for check in checks),
        }

