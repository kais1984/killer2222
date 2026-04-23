# PHASE 2 QUICK REFERENCE — INVOICING SYSTEM

## Invoice Types at a Glance

| Type | For | Rules | Revenue Recognition |
|------|-----|-------|---------------------|
| **Standard** | Direct Sales | 1 per sale, immediate | On creation |
| **Deposit** | Contracts | 1st payment, contract approval required | NOT YET (liability) |
| **Interim** | Custom Sales/Rentals | Milestones, multiple allowed | NOT YET (liability) |
| **Final** | All Contracts | Closes contract, only when ready | ON FINAL (revenue) |

---

## Creating Invoices (3 Ways)

### 1. Direct Sale Invoice
```
Sale → Click "Create Invoice" 
    → Auto-populate from sale
    → Create (standard type)
    → Revenue recognized immediately
```

### 2. Deposit Invoice
```
Contract (Approved) → Click "Create Deposit Invoice"
                   → Amount = contract.deposit_amount
                   → Creates GL liability entry
                   → Payment defers revenue
```

### 3. Contract Invoices (Interim/Final)
```
Contract (In Production) → Click "Create Interim Invoice"
                        → Amount = milestone from schedule
                        → Creates GL deferred revenue entry
                        
Contract (Ready) → Click "Create Final Invoice"
                → Amount = total - deposits - interim
                → Creates revenue entry on final GL posting
```

---

## Key Constraints

```
1. ONE SALE OR CONTRACT (not both)
2. ONLY ONE DEPOSIT PER CONTRACT
3. ONLY ONE FINAL PER CONTRACT  
4. INTERIM ONLY FOR CUSTOM TYPES
5. LOCKED FOR INVOICING AFTER FIRST INVOICE
6. IMMUTABLE ONCE POSTED (is_posted=True)
7. STATUS ALWAYS DERIVED FROM PAYMENTS
8. REVENUE ONLY ON FINAL INVOICE
```

---

## GL Posting Flow

```
Direct Sale:
  Invoice Created → GL Post (revenue immediately)
  
Deposit Invoice:
  Invoice Created → GL Post (deferred revenue = liability)
  
Interim Invoice:
  Invoice Created → GL Post (reduce liability, partial revenue? NO)
  
Final Invoice:
  Invoice Created → GL Post (full revenue recognition)
```

---

## Invoice Lifecycle State Machine

```
DRAFT (not posted)
  ↓
POSTED (is_posted=True)
  ↓
UNPAID (amount_paid=0)
  ↓
PARTIAL (0 < amount_paid < total)
  ↓
PAID (amount_paid >= total)
```

---

## Admin Actions

| Action | Admin | View | Form | URL |
|--------|-------|------|------|-----|
| List Invoices | InvoiceAdmin | InvoiceListView | - | `/sales/invoices/` |
| Create Invoice | - | InvoiceCreateView | InvoiceForm | `/sales/invoices/add/` |
| View Invoice | InvoiceAdmin | InvoiceDetailView | - | `/sales/invoices/{id}/view/` |
| Edit Invoice | InvoiceAdmin | InvoiceUpdateView | InvoiceForm | `/sales/invoices/{id}/edit/` |
| Create Deposit | - | InvoiceDepositCreateView | InvoiceDepositForm | `/sales/invoices/deposit/add/` |
| Post to GL | InvoiceAdmin | InvoicePostToGLView | - | `/sales/invoices/{id}/post-gl/` |
| Record Payment | - | PaymentRecordView | PaymentForm | `/sales/payments/add/` |

---

## Code Examples

### Create Invoice Programmatically
```python
from sales.models import Invoice
from django.utils import timezone

invoice = Invoice.objects.create(
    contract=contract,
    invoice_type='deposit',
    subtotal=contract.deposit_amount,
    tax_amount=0,
    total_amount=contract.deposit_amount,
    due_date=contract.deposit_due_date,
    created_by=request.user
)
# GL posting happens automatically
```

### Check Invoice Status
```python
invoice = Invoice.objects.get(invoice_number='INV-20260128-ABC123')

print(invoice.status)        # 'unpaid', 'partial', or 'paid'
print(invoice.amount_paid)   # Decimal from payments
print(invoice.amount_due)    # total_amount - amount_paid
print(invoice.is_posted)     # True/False (immutable if True)
```

### Record Payment
```python
from sales.models import Payment

payment = Payment.objects.create(
    sale=sale,
    amount=500.00,
    payment_method='bank_transfer',
    payment_date=timezone.now().date(),
    reference='Transfer Ref#12345',
    created_by=request.user
)
# GL posting happens automatically
```

### Validate Invoice Creation
```python
from django.core.exceptions import ValidationError

try:
    invoice = Invoice.objects.create(
        contract=contract,
        invoice_type='deposit'
        ...
    )
except ValidationError as e:
    print(f"Cannot create invoice: {e}")
```

---

## Important Fields

### Invoice Model
- `invoice_number` - Auto-generated (INV-YYYYMMDD-XXXXXX)
- `invoice_type` - standard|deposit|interim|final
- `is_posted` - Boolean, becomes immutable when True
- `gl_posted` - Boolean, indicates GL revenue recognition
- `amount_paid` - Property (sum of payments, read-only)
- `amount_due` - Property (total - paid, read-only)
- `status` - Property (unpaid|partial|paid, read-only)

### Payment Model
- `payment_number` - Auto-generated
- `payment_method` - 12 types including Stripe, Wise, ATM, etc.
- `reference` - Optional (check#, transaction ID, etc.)
- `payment_date` - Date of payment
- `created_by` - User who recorded payment

---

## Business Rules Implementation

### Can Edit Invoice?
```python
def can_edit(self):
    return not self.is_posted  # Only if not posted
```

### Can Create Deposit Invoice?
```python
# Only if:
# 1. Contract approved
# 2. Contract can invoice
# 3. No deposit invoice exists
# 4. Deposit amount > 0
```

### Can Create Final Invoice?
```python
# Only if:
# 1. Contract ready/completed
# 2. For rental: rental_end_date passed
# 3. For custom: production_end_date passed
# 4. No final invoice exists
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Invoice must have Sale OR Contract" | Missing source | Set sale OR contract (not both) |
| "Cannot modify posted invoice" | is_posted=True | Already locked, cannot edit |
| "Duplicate deposit invoice" | Multiple deposits | Check for existing deposit |
| "Contract status cannot be invoiced" | Wrong contract state | Approve/ready contract first |
| "Payment exceeds balance" | Over-payment | Reduce payment amount |

---

## Integration Checklist

- ✅ Linked to Phase 1 Contracts
- ✅ GL posting via financeaccounting
- ✅ Payment tracking integrated
- ✅ Admin interface complete
- ✅ URL routing configured
- ✅ Form validation in place
- ✅ Business rules enforced
- ✅ Audit trail maintained

---

## Next: Phase 3 (Expense Management)

Phase 3 will add:
- Expense model with categories
- GL posting for expenses
- Supplier management
- Accounts payable tracking
- Expense reporting

Ready to begin Phase 3? 🚀
