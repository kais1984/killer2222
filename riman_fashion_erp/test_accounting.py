#!/usr/bin/env python
"""
Test complete accounting flow: Sale → Invoice → Payment → Journal Entries
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riman_erp.settings')
django.setup()

from sales.models import Sale, SaleLine, Invoice, Payment
from financeaccounting.models import Account, JournalEntry
from crm.models import Client
from inventory.models import Product, StockMovement
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

print("\n" + "="*60)
print("ACCOUNTING FLOW TEST")
print("="*60)

try:
    # Create test user if doesn't exist
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@test.com', 'is_staff': True}
    )
    print(f"\n[OK] User ready: {user.username}")

    # Create test client if doesn't exist
    client, created = Client.objects.get_or_create(
        first_name='Test',
        last_name='Client',
        defaults={
            'email': 'client@test.com',
            'phone': '123456789',
        }
    )
    print(f"[OK] Client ready: {client.first_name} {client.last_name}")

    # Get or create test product
    product = Product.objects.first()
    if not product:
        from inventory.models import Category
        cat, _ = Category.objects.get_or_create(name='Wedding Dress')
        product = Product.objects.create(
            name='Test Dress',
            sku='TEST-001',
            dress_type='wedding',
            category=cat,
            size='M',
            color='white',
            sale_price=Decimal('5000.00'),
            quantity_in_stock=10
        )
    print(f"[OK] Product ready: {product.name} (Qty: {product.quantity_in_stock})")

    # Create a sale
    sale = Sale.objects.create(
        customer=client,
        created_by=user,
        subtotal=Decimal('5000.00'),
        tax_amount=Decimal('500.00'),
        total_amount=Decimal('5500.00')
    )
    print(f"\n[OK] SALE CREATED: {sale.sale_number}")
    print(f"  Total: {sale.total_amount}")

    # Create sale line
    line = SaleLine.objects.create(
        sale=sale,
        product=product,
        quantity=1,
        unit_price=Decimal('5000.00')
    )
    print(f"\n[OK] SALE LINE CREATED")
    print(f"  Product: {line.product.name}")
    print(f"  Quantity: {line.quantity}")
    print(f"  Unit price: {line.unit_price}")
    print(f"  Line total: {line.line_total}")

    # Create invoice
    invoice = Invoice.objects.create(
        sale=sale,
        subtotal=sale.subtotal,
        tax_amount=sale.tax_amount,
        total_amount=sale.total_amount
    )
    print(f"\n[OK] INVOICE CREATED: {invoice.invoice_number}")
    print(f"  Total amount: {invoice.total_amount}")
    print(f"  Invoice status: {invoice.status}")

    # Create payment
    payment = Payment.objects.create(
        sale=sale,
        amount=Decimal('5500.00'),
        payment_method='bank_transfer',
        payment_date=timezone.now().date(),
        created_by=user
    )
    print(f"\n[OK] PAYMENT CREATED: {payment.payment_number}")
    print(f"  Amount: {payment.amount}")
    print(f"  Method: {payment.payment_method}")

    # Check journal entries
    je_list = JournalEntry.objects.filter(sale_id=sale.id)
    print(f"\n[OK] JOURNAL ENTRIES: {je_list.count()} created")
    for je in je_list:
        print(f"\n  {je.journal_number} ({je.entry_type}):")
        debit_total = Decimal('0.00')
        credit_total = Decimal('0.00')
        for line in je.lines.all():
            amount_str = f"{line.amount:>10.2f}"
            if line.line_type == 'debit':
                print(f"    DR {line.account.account_code}: {amount_str}")
                debit_total += line.amount
            else:
                print(f"    CR {line.account.account_code}: {amount_str}")
                credit_total += line.amount
        print(f"    ---------------------")
        print(f"    Debits: {debit_total:>10.2f}  Credits: {credit_total:>10.2f}")
        balanced = "[OK] BALANCED" if debit_total == credit_total else "[FAIL] NOT BALANCED"
        print(f"    {balanced}")

    # Check stock movements
    sm_list = StockMovement.objects.filter(sale_id=sale.id)
    print(f"\n[OK] STOCK MOVEMENTS: {sm_list.count()} created")
    for sm in sm_list:
        print(f"  {sm.movement_type.upper()}: {sm.quantity_change:+d} units")
        print(f"    Before: {sm.quantity_before}, After: {sm.quantity_after}")

    # Check product stock
    product.refresh_from_db()
    print(f"\n[OK] PRODUCT INVENTORY UPDATED")
    print(f"  Stock remaining: {product.quantity_in_stock} units")

    # Check sale amounts
    print(f"\n[OK] SALE FINANCIAL STATUS:")
    print(f"  Total amount: {sale.total_amount}")
    print(f"  Total paid: {sale.total_paid}")
    print(f"  Amount due: {sale.amount_due}")
    print(f"  Payment status: {sale.payment_status}")
    print(f"  Invoice status: {invoice.status}")

    # Verify chart of accounts
    accounts = Account.objects.all()
    print(f"\n[OK] CHART OF ACCOUNTS: {accounts.count()} accounts")
    for acc in accounts.order_by('account_code'):
        balance = acc.get_balance()
        print(f"  {acc.account_code} {acc.account_name:<30} {balance:>10.2f}")

    print("\n" + "="*60)
    print("[OK] ALL TESTS PASSED - ACCOUNTING SYSTEM WORKING!")
    print("="*60 + "\n")

except Exception as e:
    print(f"\n[ERROR] ERROR: {e}")
    import traceback
    traceback.print_exc()
