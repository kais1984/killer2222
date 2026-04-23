# NEXT STEPS: GET PHASE 1 LIVE

## IMMEDIATE ACTIONS (Today)

### 1. Run Migrations ⚠️ CRITICAL

```bash
cd C:\Users\KAIS\Documents\RIAMAN_FASHION_ERP\riman_fashion_erp

# Create migration files
python manage.py makemigrations financeaccounting
python manage.py makemigrations sales

# Review migration files (check riman_fashion_erp/financeaccounting/migrations/)
# Should show:
# - Adding expense_id field to JournalEntry
# - Adding status field to JournalEntry
# - Adding is_balanced() method (no migration needed - it's a method)

# Apply migrations
python manage.py migrate
```

### 2. Create GL Accounts (Chart of Accounts) ⚠️ CRITICAL

**Option A: Via Django Admin**
```
1. Start server: python manage.py runserver
2. Go to http://localhost:8000/admin/
3. Login with admin credentials
4. Navigate to Chart of Accounts (or Accounts)
5. Add each account:
```

| Code | Name | Type | Subtype | Active |
|------|------|------|---------|--------|
| 1000 | Cash | asset | cash | ✓ |
| 1050 | Undeposited Funds | asset | cash | ✓ |
| 1100 | Inventory | asset | inventory | ✓ |
| 1200 | Accounts Receivable | asset | accounts_receivable | ✓ |
| 2200 | Sales Tax Payable | liability | sales_tax | ✓ |
| 4100 | Sales Revenue | revenue | sales | ✓ |
| 5100 | Cost of Goods Sold | expense | cogs | ✓ |
| 6100 | Operating Expenses | expense | operating | ✓ |
| 6200 | Marketing Expense | expense | marketing | ✓ |
| 6300 | Maintenance & Cleaning | expense | maintenance | ✓ |
| 6400 | Administrative Expenses | expense | administrative | ✓ |

**Option B: Via Script**
```bash
# Create create_gl_accounts.py in manage.py directory
python manage.py shell < create_gl_accounts.py
```

### 3. Test the Flow

```bash
# In Django shell:
python manage.py shell

# Create test data:
from sales.models import Sale, SaleLine, Invoice, Payment
from inventory.models import Product
from crm.models import Client
from financeaccounting.models import JournalEntry
from decimal import Decimal

# Get or create test data
client = Client.objects.first() or Client.objects.create(first_name="Test", last_name="Customer", email="test@test.com")
product = Product.objects.first()

# Create sale
sale = Sale.objects.create(customer=client, subtotal=100, tax_amount=10, total_amount=110)

# Add line item
line = SaleLine.objects.create(
    sale=sale, 
    product=product, 
    quantity=1, 
    unit_price=100,
    line_total=100
)

# Create invoice (should auto-post GL entries)
invoice = Invoice.objects.create(
    sale=sale,
    subtotal=100,
    tax_amount=10,
    total_amount=110
)

# Check if entries were posted
entries = JournalEntry.objects.filter(sale_id=sale.id)
print(f"Entries created: {entries.count()}")
for entry in entries:
    print(f"  {entry.journal_number}: {entry.entry_type}")
    print(f"  Balanced: {entry.is_balanced()}")

# Record payment
payment = Payment.objects.create(
    sale=sale,
    amount=110,
    payment_method='bank',
    payment_date='2026-01-26'
)

# Check payment entry
payment_entries = JournalEntry.objects.filter(payment_id=payment.id)
print(f"Payment entries: {payment_entries.count()}")

# Exit shell
exit()
```

---

## VERIFICATION CHECKLIST

After migrations and GL account setup:

- [ ] Can create sale with line items
- [ ] Can create invoice without errors
- [ ] Journal entries appear for invoice
- [ ] All entries are balanced (is_balanced() == True)
- [ ] Can record payment without errors
- [ ] Journal entry appears for payment
- [ ] Invoice status changes to "paid" or "partial"
- [ ] AR balance reflects outstanding amount
- [ ] Trial balance balances (debits == credits)

---

## COMMON SETUP ISSUES & FIXES

### Issue: "Required GL account not configured"

**Cause**: Accounts table is empty

**Fix**:
1. Create Chart of Accounts via admin
2. Verify account codes match SaleAccountingService.ACCOUNT_CODES
3. Ensure is_active=True for all accounts

### Issue: AttributeError: 'Account' has no attribute 'get_balance'

**Cause**: Account model missing get_balance() method

**Fix**: Already in financeaccounting/models.py. If still missing:
```python
# In Account model, add:
def get_balance(self):
    from django.db.models import Sum
    debits = self.journalentryline_set.filter(line_type='debit').aggregate(Sum('amount'))['amount__sum'] or 0
    credits = self.journalentryline_set.filter(line_type='credit').aggregate(Sum('amount'))['amount__sum'] or 0
    if self.account_type in ['asset', 'expense']:
        return debits - credits
    else:
        return credits - debits
```

### Issue: Invoice creation succeeds but no GL entries

**Cause**: Accounting service not being called

**Fix**:
1. Check Invoice.save() includes service calls (already added)
2. Check financeaccounting/services.py exists
3. Check for exceptions in logs: `tail -f logs/django.log`
4. Manually call service in Django shell (see Testing section)

### Issue: "Account.objects.get(account_code='1200') not found"

**Cause**: Account doesn't exist or wrong code

**Fix**:
1. Check SaleAccountingService.ACCOUNT_CODES matches your GL codes
2. Create missing accounts in admin
3. Or update ACCOUNT_CODES to match existing accounts

---

## LOGGING & DEBUGGING

### Enable Detailed Logging

Create `settings.py` addition:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
}
```

Then check logs:
```bash
tail -f logs/django.log
```

### Check Database Directly

```bash
# SQLite (if using SQLite)
python manage.py dbshell

# Then query:
SELECT * FROM financeaccounting_account;
SELECT * FROM financeaccounting_journalentry WHERE sale_id='...' LIMIT 5;
SELECT * FROM financeaccounting_journalentryline;
```

---

## DEPLOYMENT STEPS

### Step 1: Backup Database

```bash
# If using SQLite
cp db.sqlite3 db.sqlite3.backup.2026-01-26

# If using PostgreSQL
pg_dump dbname > backup.sql
```

### Step 2: Apply Migrations

```bash
python manage.py migrate
```

### Step 3: Create Superuser (if needed)

```bash
python manage.py createsuperuser
# or
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'password')" | python manage.py shell
```

### Step 4: Create GL Accounts

Use admin or script (see above)

### Step 5: Test Complete Flow

```bash
python manage.py shell
# Run test scenario (see above)
```

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 7: Run Server

```bash
python manage.py runserver
```

### Step 8: Verify in Browser

1. Login to admin: http://localhost:8000/admin/
2. Check Chart of Accounts
3. Check Journal Entries (should be empty)
4. Create test sale and verify entries appear

---

## ROLLBACK PLAN (IF PROBLEMS)

### If Migrations Fail

```bash
# Revert last migration
python manage.py migrate financeaccounting 0001_initial
python manage.py migrate sales 0001_initial

# Or go back further
python manage.py migrate financeaccounting zero
```

### If GL Posting Fails

- Invoices still create (errors logged)
- Payments still record (errors logged)
- Manually post entries later via Django shell
- No data loss

### If Database Corrupted

```bash
# Restore backup
cp db.sqlite3.backup.2026-01-26 db.sqlite3

# Or for PostgreSQL
psql dbname < backup.sql
```

---

## FINAL CHECKLIST BEFORE GOING LIVE

- [ ] Migrations applied successfully
- [ ] Chart of Accounts created (11+ accounts)
- [ ] Test sale → invoice → payment flow works
- [ ] Journal entries created and balanced
- [ ] Trial balance balances
- [ ] No errors in logs
- [ ] Backup created
- [ ] Staff trained on new GL posting
- [ ] Admin understands reversal process
- [ ] Monitoring/alerts set up for posting errors

---

## FILES TO REVIEW BEFORE GOING LIVE

1. **financeaccounting/services.py** - Core accounting logic
2. **financeaccounting/models.py** - GL models, is_balanced() method
3. **sales/models.py** - Invoice.save() and Payment.save() hooks
4. **riman_erp/settings.py** - Logging configuration
5. **PHASE_1_COMPLETE.md** - Technical documentation
6. **QUICK_REFERENCE.md** - Developer guide

---

## SUPPORT RESOURCES

📞 **If stuck**:
1. Check QUICK_REFERENCE.md for common issues
2. Check financeaccounting/services.py docstrings
3. Review PHASE_1_COMPLETE.md for architecture
4. Check Django logs for error details
5. Test in Django shell

📚 **Learning**:
- Double-entry accounting: https://en.wikipedia.org/wiki/Double-entry_bookkeeping
- Django models: https://docs.djangoproject.com/en/6.0/topics/db/models/
- Django testing: https://docs.djangoproject.com/en/6.0/topics/testing/

---

## TIMELINE

- **Today (Jan 26)**: 
  - Run migrations
  - Create GL accounts
  - Test flow
  
- **Tomorrow (Jan 27)**:
  - Final verification
  - Staff training
  - Go live

---

## WHAT'S COMPLETE (Phase 1)

✅ Core business flow (Sale → Invoice → Payment → GL)
✅ Automatic GL posting (no manual entries)
✅ Double-entry enforcement
✅ Reversal support
✅ Immutability (no edits, only reversals)
✅ Error handling & validation
✅ Audit trail (who, when, what)
✅ Trial balance balancing
✅ COGS tracking

---

## WHAT'S NEXT (Phases 2-11)

📋 Phase 2: Expense system (ready, needs testing)
📋 Phase 3: Financial reporting (ready, needs implementation)
📋 Phase 4: Mobile design (partial, needs completion)
📋 Phase 5: Print/PDF (not started)
📋 Phase 6+: Other features

---

**Created**: January 26, 2026
**Status**: READY FOR DEPLOYMENT
**Next Review**: After live testing (Jan 27)

Good luck! 🚀
