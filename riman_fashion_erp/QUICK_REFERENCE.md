# RIMAN FASHION ERP - QUICK REFERENCE GUIDE
**Phase 1: Core Business Flow - For Developers**

---

## FILE STRUCTURE

### Key Files Modified/Created

```
riman_fashion_erp/
├── financeaccounting/
│   ├── models.py                 ✅ Updated (JournalEntry, is_balanced())
│   ├── services.py              ✨ NEW (SaleAccountingService, ExpenseAccountingService)
│   └── views.py                 (Update later for reporting)
│
├── sales/
│   ├── models.py                ✅ Updated (Invoice.save(), Payment.save())
│   ├── views.py
│   └── urls.py
│
├── inventory/
│   └── models.py                ✅ Already has cost_price field
│
├── accounting/
│   └── models.py                ✅ Already has Expense model
│
├── IMPLEMENTATION_PLAN.md       ✨ NEW (11-phase roadmap)
├── PHASE_1_COMPLETE.md          ✨ NEW (This phase summary)
└── QUICK_REFERENCE.md           ✨ NEW (This file)
```

---

## HOW TO USE THE ACCOUNTING SERVICE

### Import the Service

```python
from financeaccounting.services import SaleAccountingService, ExpenseAccountingService
```

### Automatic GL Posting (NO MANUAL CALLS NEEDED)

The services are called automatically from model.save():

```python
# Create a sale and invoice
sale = Sale.objects.create(customer=client, ...)
sale_line = SaleLine.objects.create(sale=sale, product=product, quantity=2, unit_price=100)

# Create invoice
invoice = Invoice.objects.create(
    sale=sale,
    subtotal=sale.subtotal,
    tax_amount=sale.tax_amount,
    total_amount=sale.total_amount
)
# ✅ Automatically posts:
#    - Journal Entry 1: Revenue recognition
#    - Journal Entry 2 & 3: COGS & inventory

# Record payment
payment = Payment.objects.create(
    sale=sale,
    amount=invoice.total_amount,
    payment_method='bank',
    payment_date=today
)
# ✅ Automatically posts:
#    - Journal Entry 4: Cash collection
```

### Manual GL Posting (FOR ADVANCED USAGE)

If you need to manually trigger posting:

```python
from financeaccounting.services import SaleAccountingService

# Post revenue entry
try:
    je1 = SaleAccountingService.post_invoice(invoice)
    print(f"Posted: {je1.journal_number}")
except AccountingEntryError as e:
    print(f"Error: {e}")

# Post COGS for each line
for line in sale.lines.all():
    try:
        je2 = SaleAccountingService.post_stock_movement(line)
        print(f"Posted: {je2.journal_number}")
    except AccountingEntryError as e:
        print(f"Error: {e}")

# Post payment
try:
    je3 = SaleAccountingService.post_payment(payment)
    print(f"Posted: {je3.journal_number}")
except AccountingEntryError as e:
    print(f"Error: {e}")
```

---

## GL ACCOUNT CODES (CONFIGURABLE)

Edit in: `financeaccounting/services.py` → `SaleAccountingService.ACCOUNT_CODES`

```python
ACCOUNT_CODES = {
    'accounts_receivable': '1200',  # AR when invoice created
    'sales_revenue': '4100',        # Revenue recognized
    'sales_tax_payable': '2200',    # Tax on sale
    'inventory': '1100',            # Inventory value
    'cogs': '5100',                 # Cost of goods sold
    'cash': '1000',                 # Cash in
    'undeposited_funds': '1050',    # Pending deposits
}
```

**To use different account codes**:
1. Update the codes in services.py
2. Ensure accounts exist in Chart of Accounts
3. Run migrations if database schema changed

---

## VALIDATION & ERROR HANDLING

### Payment Validation (Prevents Overpayment)

```python
# This will raise ValidationError
payment = Payment(
    sale=sale,        # Total = $100
    amount=150,       # > $100
    payment_date=today
)
payment.full_clean()  # ❌ Raises ValidationError
```

### Journal Entry Validation (Ensures Balanced)

```python
# If entry is not balanced:
je = JournalEntry.objects.create(...)
je.lines.create(account=account1, line_type='debit', amount=100)
je.save()  # ✅ Calls clean() which validates balance

# Check if balanced:
is_balanced = je.is_balanced()  # True or False
```

### GL Account Existence Check

```python
# If GL account not configured:
try:
    SaleAccountingService.post_invoice(invoice)
except AccountingEntryError as e:
    # "Required GL account not configured: 1200"
    print(e)
```

---

## REVERSALS & CORRECTIONS

### Reverse a Payment

```python
# Original payment
payment1 = Payment.objects.create(
    sale=sale,
    amount=100,
    payment_method='bank',
    payment_date=today
)
# ✅ Creates JE: Debit Cash 100, Credit AR 100

# Reverse it (e.g., for refund)
reversal_payment = Payment.objects.create(
    sale=sale,
    amount=100,
    payment_method='bank',
    payment_date=tomorrow,
    reversed_by=None  # Will be updated
)

# Link the reversal
payment1.reversed_by = reversal_payment
payment1.save()

# ✅ Creates offset JE: Debit AR 100, Credit Cash 100
# Result: Net effect cancels, but both entries remain in ledger
```

### Check if Payment is Reversed

```python
if payment1.is_reversed():
    reversal = payment1.reversed_by
    print(f"Reversed by: {reversal.payment_number}")
```

---

## QUERYING JOURNAL ENTRIES

### Get All Entries for a Sale

```python
from financeaccounting.models import JournalEntry

sale_entries = JournalEntry.objects.filter(sale_id=sale.id)
for entry in sale_entries:
    print(f"{entry.journal_number}: {entry.get_entry_type_display()}")
    for line in entry.lines.all():
        print(f"  {line.account}: {line.get_line_type_display()} {line.amount}")
```

### Get GL Account Balance

```python
from financeaccounting.models import Account

ar_account = Account.objects.get(account_code='1200')
balance = ar_account.get_balance()
print(f"AR Balance: ${balance}")
```

### Verify Trial Balance

```python
from django.db.models import Sum
from financeaccounting.models import JournalEntryLine

total_debits = JournalEntryLine.objects.filter(
    line_type='debit'
).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

total_credits = JournalEntryLine.objects.filter(
    line_type='credit'
).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

if total_debits == total_credits:
    print(f"✅ Trial Balance Balanced: ${total_debits}")
else:
    print(f"❌ Out of Balance - Debits: ${total_debits}, Credits: ${total_credits}")
```

---

## TESTING CHECKLIST

### Test 1: Simple Sale & Payment

```python
from django.test import TestCase
from sales.models import Sale, SaleLine, Invoice, Payment
from financeaccounting.models import JournalEntry

class SaleAccountingTest(TestCase):
    def test_complete_sale_flow(self):
        # Create sale
        sale = Sale.objects.create(
            customer=self.client,
            subtotal=100,
            tax_amount=10,
            total_amount=110
        )
        
        # Create line item
        SaleLine.objects.create(
            sale=sale,
            product=self.product,
            quantity=1,
            unit_price=100,
            line_total=100
        )
        
        # Create invoice
        invoice = Invoice.objects.create(
            sale=sale,
            subtotal=100,
            tax_amount=10,
            total_amount=110
        )
        
        # Check journal entries created
        sale_entries = JournalEntry.objects.filter(sale_id=sale.id)
        self.assertEqual(sale_entries.count(), 3)  # Revenue + 2 COGS
        
        # Check entries are balanced
        for entry in sale_entries:
            self.assertTrue(entry.is_balanced())
        
        # Record payment
        payment = Payment.objects.create(
            sale=sale,
            amount=110,
            payment_method='bank',
            payment_date=today
        )
        
        # Check payment entry created
        payment_entries = JournalEntry.objects.filter(payment_id=payment.id)
        self.assertEqual(payment_entries.count(), 1)
```

### Test 2: Overpayment Prevention

```python
def test_prevent_overpayment(self):
    sale = Sale.objects.create(total_amount=100)
    
    payment = Payment(
        sale=sale,
        amount=150,  # > total
        payment_date=today
    )
    
    with self.assertRaises(ValidationError):
        payment.full_clean()
```

### Test 3: Trial Balance

```python
def test_trial_balance(self):
    # Create multiple sales, payments, expenses
    # Then verify:
    total_debits = sum(...)
    total_credits = sum(...)
    self.assertEqual(total_debits, total_credits)
```

---

## DEBUGGING TIPS

### Check If Invoice Posted

```python
from financeaccounting.models import JournalEntry

# Find invoice's journal entries
entries = JournalEntry.objects.filter(
    sale_id=invoice.sale.id,
    entry_type='sale'
)

if entries.exists():
    entry = entries.first()
    print(f"Invoice Posted: {entry.journal_number}")
    print(f"Status: {entry.status}")
    for line in entry.lines.all():
        print(f"  {line.account}: {line.line_type} {line.amount}")
else:
    print("Invoice NOT posted to GL")
```

### Check AR Balance

```python
from financeaccounting.models import Account

ar = Account.objects.get(account_code='1200')
balance = ar.get_balance()

print(f"AR Balance: ${balance}")
print(f"Expected (from invoices): ${sum_of_unpaid_invoices()}")

if balance != sum_of_unpaid_invoices():
    print("⚠️  Reconciliation issue!")
```

### View All Entries for a Payment

```python
from financeaccounting.models import JournalEntry

entries = JournalEntry.objects.filter(payment_id=payment.id)
for entry in entries:
    print(f"\n{entry.journal_number}")
    print(f"Type: {entry.entry_type}")
    print(f"Date: {entry.entry_date}")
    for line in entry.lines.all():
        print(f"  {line.account.account_code} | {line.line_type} | ${line.amount}")
```

---

## COMMON ISSUES & FIXES

### Issue 1: GL Account Not Configured

**Error**: `AccountingEntryError: Required GL account not configured: 1200`

**Fix**:
```python
# In Django admin, create account:
Account.objects.create(
    account_code='1200',
    account_name='Accounts Receivable',
    account_type='asset',
    account_subtype='accounts_receivable',
    is_active=True
)
```

### Issue 2: Invoice Not Posting

**Debug**:
```python
# Check logs
import logging
logger = logging.getLogger('sales.models')

# Or manually try to post
from financeaccounting.services import SaleAccountingService
try:
    je = SaleAccountingService.post_invoice(invoice)
    print(f"Posted: {je.journal_number}")
except Exception as e:
    print(f"Error: {e}")
```

### Issue 3: Trial Balance Out of Balance

**Check**:
```python
# Find the problem entry
from financeaccounting.models import JournalEntry

for entry in JournalEntry.objects.filter(status='posted'):
    if not entry.is_balanced():
        print(f"Unbalanced: {entry.journal_number}")
        for line in entry.lines.all():
            print(f"  {line.account}: {line.line_type} {line.amount}")
```

---

## NEXT STEPS (AFTER PHASE 1)

### Phase 2: Expense System
- Implement `ExpenseAccountingService.post_expense()` fully
- Test expense categories & GL mapping
- Add expense reversal logic

### Phase 3: Financial Reporting
- Build trial balance report
- Build income statement (P&L)
- Build balance sheet
- Build cash flow statement

### Phase 4: Mobile & Print
- Make invoice printable
- Create print-ready templates
- Add PDF export
- Mobile-friendly forms

---

## SUPPORT & DOCUMENTATION

📁 **Files to Reference**:
- IMPLEMENTATION_PLAN.md - Full 11-phase roadmap
- PHASE_1_COMPLETE.md - Detailed Phase 1 summary
- QUICK_REFERENCE.md - This file
- financeaccounting/services.py - Service code
- sales/models.py - Model code

📚 **Django Documentation**:
- https://docs.djangoproject.com/en/6.0/
- https://docs.djangoproject.com/en/6.0/topics/db/models/

🔍 **Debugging**:
- `python manage.py shell` - Interactive Django shell
- `python manage.py dbshell` - Direct database access
- Django Admin - View/edit models directly

---

**Last Updated**: January 26, 2026  
**Status**: PHASE 1 COMPLETE  
**Next Phase**: Expense System (Ready to implement)
