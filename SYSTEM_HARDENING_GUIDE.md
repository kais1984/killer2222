# SYSTEM HARDENING & PROFESSIONALIZATION GUIDE
## Refining Phase 1-3 for Production Grade

**Date:** January 28, 2026  
**Focus:** Elevate existing implementation to architectural standards  
**Target:** Production-ready, contract-centric luxury ERP  

---

## 📋 EXECUTIVE SUMMARY

The existing implementation (Phase 1-3) has solid foundations:
- ✅ Contract model with lifecycle (Phase 1)
- ✅ Invoice model with types and GL posting (Phase 2)
- ✅ Expense management with workflow (Phase 3)

**This guide hardens these systems to production grade by:**
1. Enforcing architectural rules at the model level
2. Adding missing constraints and validations
3. Completing the service layer for business logic
4. Implementing comprehensive error handling
5. Adding audit trail completeness
6. Preparing for advanced reporting

---

## 🔧 REFINEMENT 1: CONTRACT MODEL HARDENING

### Current State → Enhanced State

**What to Add:**

```python
# accounting/models.py - Enhance Contract Model

Additional Fields:
  design_specs          → JSONField (for custom contracts)
  measurements          → JSONField (custom tailoring details)
  late_return_penalty   → DecimalField (daily fine for late returns)
  damage_clause_amount  → DecimalField (max damage liability)
  contract_value        → DecimalField (total contract worth, calculated)
  revenue_schedule      → JSONField (when revenue is recognized)

Methods to Add:
  get_revenue_schedule()       → Returns [date, amount] pairs
  get_unrecognized_revenue()   → Deposits held as liability
  get_recognized_revenue()     → Amount recognized to P&L
  validate_rental_dates()      → Check no overlaps for product
  validate_custom_specs()      → Ensure design_specs if custom
  lock_after_first_invoice()   → Prevent spec changes
  get_deposit_amount()         → Security deposit or deposit invoice
```

**Implementation Priority:** HIGH  
**Effort:** 2-3 hours  
**Impact:** Makes contracts true source of truth

---

## 🔧 REFINEMENT 2: INVOICE MODEL HARDENING

### Current State → Enhanced State

**What to Add:**

```python
# sales/models.py - Enhance Invoice Model

Additional Fields:
  revenue_account       → FK to GLAccount (which account to credit)
  revenue_recognized    → BooleanField (revenue posted to GL)
  recognized_at         → DateTimeField (when revenue recognized)
  recognized_by         → FK User (who recognized revenue)
  contract_ref          → Auto-populate from contract
  deposit_invoice       → BooleanField (is this a deposit invoice)
  final_invoice         → BooleanField (is this the final invoice)

Methods to Add:
  recognize_revenue()              → Post revenue to GL
  check_revenue_recognition_rules() → Validate timing
  is_revenue_recognizable()        → Can this invoice recognize revenue?
  get_unearned_portion()           → For deposits (liability)
  get_earned_portion()             → For current period revenue
  create_offset_entry_for_reversal() → GL reversal if canceled
```

**Implementation Priority:** HIGH  
**Effort:** 2-3 hours  
**Impact:** Revenue recognition becomes rule-driven, not manual

---

## 🔧 REFINEMENT 3: INVENTORY MODEL HARDENING

### Current State → Enhanced State

**What to Add:**

```python
# inventory/models.py - Complete Inventory Model

Create StockMovement Model (Immutable Audit Trail):
  product              → FK Product
  movement_type        → ['purchase', 'sale', 'reserve', 'release', 'production', 'return', 'adjustment']
  quantity_changed     → Integer (positive or negative)
  quantity_before      → Integer (snapshot for audit)
  quantity_after       → Integer (snapshot for audit)
  reference_id         → FK to Contract or Sale (never null)
  reference_type       → ['contract', 'sale', 'stock_adjustment']
  notes                → TextField
  created_at           → DateTimeField (auto_now_add)
  created_by           → FK User
  
  Constraints:
    ✓ Never edit or delete (audit trail immutable)
    ✓ quantity_changed is never zero
    ✓ reference_id and reference_type always set
    ✓ quantity_after = quantity_before + quantity_changed

Enhance Product Model:
  quantity_in_stock    → DecimalField (always read from movements)
  quantity_reserved    → DecimalField (always read from movements)
  quantity_on_order    → DecimalField (always read from movements)
  last_cost_price      → DecimalField (FIFO costing)
  inventory_value      → Property (quantity_in_stock * last_cost_price)
  
  Methods:
    get_available_qty()  → quantity_in_stock - quantity_reserved
    can_sell(qty)        → qty <= get_available_qty()
    can_reserve(qty)     → qty <= quantity_in_stock
    get_cost_value()     → For balance sheet (GL account 1200)
```

**Implementation Priority:** HIGH  
**Effort:** 3-4 hours  
**Impact:** Inventory becomes immutable, auditable, always accurate

---

## 🔧 REFINEMENT 4: GL POSTING COMPLETENESS

### Current State → Enhanced State

**What to Add:**

```python
# financeaccounting/models.py - Complete GL Integration

Enhance JournalEntry:
  entry_type          → Expand choices ['sale', 'invoice', 'payment', 'expense', 'adjustment', 'reversal']
  related_sale        → FK to Sale (if sale-related)
  related_invoice     → FK to Invoice (if invoice-related)
  related_expense     → FK to Expense (if expense-related)
  related_entry       → FK to JournalEntry (if reversal)
  is_reversal_of      → FK to JournalEntry (points to original)
  
  Methods:
    reverse()         → Create offsetting entry
    verify_balance()  → Ensure debits = credits
    get_total_debits() → Sum of all debit lines
    get_total_credits() → Sum of all credit lines

Create RevenueRecognitionLog:
  contract          → FK Contract
  invoice           → FK Invoice
  transaction_type  → ['deposit_received', 'revenue_recognized', 'revenue_reversed']
  amount            → Amount recognized
  account_debited   → GL account (AR or Cash)
  account_credited  → GL account (Unearned or Revenue)
  recognized_date   → When recognized
  recognized_by     → User
  notes             → Why/when recognized (per contract terms)
```

**Implementation Priority:** CRITICAL  
**Effort:** 2-3 hours  
**Impact:** Every transaction traceable to rule-based GL posting

---

## 🔧 REFINEMENT 5: SERVICE LAYER COMPLETION

### Current State → Enhanced State

**Create Comprehensive Services:**

```python
# financeaccounting/services.py - Enhanced Service Layer

class ContractRevenueService:
  """Handles all revenue recognition logic based on contract type"""
  
  @staticmethod
  def get_revenue_schedule(contract):
    """Returns list of [date, amount] when revenue should be recognized"""
    if contract.type == 'rental':
      # Recognize on rental start or monthly
      return [(contract.start_date, contract.amount)]
    elif contract.type == 'custom_sale':
      # Deposits are liability, final invoice only
      return [(contract.completion_date, contract.total_value - deposit)]
    elif contract.type == 'custom_rent':
      # Deposit as liability, rental revenue per terms
      return [(contract.start_date, contract.rental_amount)]
  
  @staticmethod
  def recognize_revenue_for_invoice(invoice):
    """Check if invoice qualifies for revenue recognition"""
    contract = invoice.contract
    if not contract:
      # Direct sales: recognize immediately
      return True
    
    if contract.type == 'custom_sale':
      # Only recognize on final invoice
      return invoice.invoice_type == 'final'
    
    elif contract.type == 'rental':
      # Recognize per contract terms
      return invoice.invoice_date >= contract.start_date
    
    else:
      return True
  
  @staticmethod
  def post_revenue_entry(invoice):
    """Create GL entry for revenue recognition"""
    if not ContractRevenueService.recognize_revenue_for_invoice(invoice):
      raise ValueError("Invoice not eligible for revenue recognition")
    
    # Create journal entry
    # Debit: AR or Cash
    # Credit: Revenue account or Unearned
    
    # Record in RevenueRecognitionLog

class InventoryService:
  """Manages all inventory movements (immutable audit trail)"""
  
  @staticmethod
  def reserve_stock(product, quantity, contract, notes=""):
    """Reserve stock for rental or custom order"""
    available = product.get_available_qty()
    if quantity > available:
      raise ValueError(f"Cannot reserve {quantity}. Only {available} available.")
    
    StockMovement.create(
      product=product,
      movement_type='reserve',
      quantity_changed=-quantity,
      reference_id=contract.id,
      reference_type='contract',
      notes=notes
    )
  
  @staticmethod
  def reduce_stock(product, quantity, sale, notes=""):
    """Reduce stock for direct sale"""
    if quantity > product.quantity_in_stock:
      raise ValueError("Insufficient stock")
    
    StockMovement.create(
      product=product,
      movement_type='sale',
      quantity_changed=-quantity,
      reference_id=sale.id,
      reference_type='sale',
      notes=notes
    )
  
  @staticmethod
  def return_stock(product, quantity, contract, notes=""):
    """Return rented product back to available stock"""
    StockMovement.create(
      product=product,
      movement_type='return',
      quantity_changed=quantity,
      reference_id=contract.id,
      reference_type='contract',
      notes=notes
    )

class ContractValidationService:
  """Enforces all contract rules before creating transactions"""
  
  @staticmethod
  def validate_before_invoice_creation(contract):
    """Check if contract is ready for invoicing"""
    if contract.status != 'approved':
      raise ValueError("Contract must be approved before invoicing")
    
    if contract.type == 'rental':
      if not ContractValidationService.check_rental_dates_valid(contract):
        raise ValueError("Rental dates conflict with another reservation")
    
    if contract.type in ['custom_sale', 'custom_rent']:
      if not contract.design_specs:
        raise ValueError("Custom contract must have design specifications")
    
    return True
  
  @staticmethod
  def check_rental_dates_valid(contract):
    """Ensure no overlapping rentals for same product"""
    overlaps = Contract.objects.filter(
      product=contract.product,
      type='rental',
      start_date__lt=contract.end_date,
      end_date__gt=contract.start_date,
      status='approved'
    ).exclude(id=contract.id)
    
    return not overlaps.exists()
```

**Implementation Priority:** CRITICAL  
**Effort:** 4-5 hours  
**Impact:** Business logic centralized, testable, rule-enforced

---

## 🔧 REFINEMENT 6: AUDIT TRAIL COMPLETENESS

### Current State → Enhanced State

**Add to All Models:**

```python
# Every model that affects GL or data must have:

class BaseAuditedModel(models.Model):
  created_by          → FK User (auto-set on create)
  created_at          → DateTimeField (auto_now_add)
  updated_by          → FK User (auto-set on update)
  updated_at          → DateTimeField (auto_now)
  
  class Meta:
    abstract = True
  
  def save(self, *args, user=None, **kwargs):
    """Override save to track user"""
    if user:
      if not self.pk:
        self.created_by = user
      self.updated_by = user
    super().save(*args, **kwargs)

# Add to:
  ✓ Contract
  ✓ Sale
  ✓ Invoice
  ✓ Payment
  ✓ Expense
  ✓ StockMovement (immutable: created_by, created_at)
  ✓ JournalEntry
```

**Implementation Priority:** MEDIUM  
**Effort:** 1-2 hours  
**Impact:** Complete traceability of all changes

---

## 🔧 REFINEMENT 7: ERROR HANDLING & VALIDATION

### Current State → Enhanced State

**Add Comprehensive Error Handling:**

```python
# Create custom exceptions

class RimanERP_Error(Exception):
  """Base exception for all ERP errors"""
  pass

class ContractError(RimanERP_Error):
  """Contract-related errors"""
  pass

class InventoryError(RimanERP_Error):
  """Inventory errors (insufficient stock, overlap, etc.)"""
  pass

class RevenueRecognitionError(RimanERP_Error):
  """Revenue recognition errors (premature, invalid type)"""
  pass

class GLError(RimanERP_Error):
  """GL posting errors (imbalance, invalid account)"""
  pass

class ValidationError(RimanERP_Error):
  """Data validation errors"""
  pass

# Every transaction method catches and logs:

def create_invoice(contract, invoice_type):
  try:
    # 1. Validate contract
    ContractValidationService.validate_before_invoice_creation(contract)
    
    # 2. Validate business rules
    if invoice_type == 'final':
      if not contract.is_production_complete():
        raise ContractError("Production not complete for final invoice")
    
    # 3. Create invoice
    invoice = Invoice.create(...)
    
    # 4. Post to GL
    InvoiceAccountingService.post_invoice(invoice)
    
    # 5. Return result
    return invoice
    
  except ContractError as e:
    logger.error(f"Contract validation failed: {e}")
    raise
  except InventoryError as e:
    logger.error(f"Inventory error: {e}")
    raise
  except GLError as e:
    logger.error(f"GL posting failed: {e}")
    # Rollback invoice if GL failed
    invoice.delete()
    raise
  except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise
```

**Implementation Priority:** HIGH  
**Effort:** 2-3 hours  
**Impact:** Prevents bad data, clear error messages, proper rollback

---

## 🔧 REFINEMENT 8: API LAYER HARDENING

### Current State → Enhanced State

**Add to Views/APIs:**

```python
# sales/views.py - Add to InvoiceCreateView

class InvoiceCreateView(LoginRequiredMixin, CreateView):
  def post(self, request, *args, **kwargs):
    try:
      # 1. Get contract
      contract = Contract.objects.get(pk=request.POST.get('contract_id'))
      
      # 2. Validate
      ContractValidationService.validate_before_invoice_creation(contract)
      
      # 3. Determine invoice type
      invoice_type = self.determine_invoice_type(contract)
      
      # 4. Calculate amounts
      amounts = self.calculate_amounts(contract, invoice_type)
      
      # 5. Create invoice
      invoice = Invoice.objects.create(
        contract=contract,
        invoice_type=invoice_type,
        amount=amounts['total'],
        ...
      )
      
      # 6. Reserve inventory (if rental/custom)
      if contract.type in ['rental', 'custom_rent']:
        InventoryService.reserve_stock(
          contract.product,
          1,  # qty
          contract,
          f"Reservation from invoice {invoice.invoice_number}"
        )
      
      # 7. Post to GL
      InvoiceAccountingService.post_invoice(invoice, request.user)
      
      # 8. Lock contract if final invoice
      if invoice_type == 'final':
        contract.lock_for_invoicing()
      
      messages.success(request, f"Invoice {invoice.invoice_number} created")
      return redirect('invoice_detail', pk=invoice.pk)
      
    except ContractError as e:
      messages.error(request, f"Contract error: {e}")
      return self.form_invalid(form)
    except InventoryError as e:
      messages.error(request, f"Inventory error: {e}")
      return self.form_invalid(form)
    except GLError as e:
      messages.error(request, f"Accounting error: {e}")
      return self.form_invalid(form)
```

**Implementation Priority:** HIGH  
**Effort:** 2-3 hours  
**Impact:** Reliable API, proper error messages, data consistency

---

## 🔧 REFINEMENT 9: ADMIN INTERFACE PROFESSIONALIZATION

### Current State → Enhanced State

**Enhance Admin Classes:**

```python
# accounting/admin.py - Professional Admin

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
  list_display = [
    'contract_number',
    'contract_type',
    'customer',
    'status_badge',
    'total_value',
    'approval_status',
    'revenue_status'
  ]
  
  fieldsets = (
    ('Identification', {
      'fields': ('contract_number', 'contract_type', 'status')
    }),
    ('Parties', {
      'fields': ('customer', 'notes')
    }),
    ('For Rental Contracts', {
      'fields': ('product', 'start_date', 'end_date', 'security_deposit', 'late_return_penalty'),
      'classes': ('collapse',)
    }),
    ('For Custom Contracts', {
      'fields': ('design_specs', 'measurements', 'completion_date'),
      'classes': ('collapse',)
    }),
    ('Financial', {
      'fields': ('total_value', 'payment_terms', 'revenue_schedule'),
      'classes': ('collapse',)
    }),
    ('Approvals', {
      'fields': ('approved_by', 'approved_at'),
      'readonly_fields': ('approved_by', 'approved_at'),
      'classes': ('collapse',)
    }),
    ('Audit', {
      'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
      'readonly_fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
      'classes': ('collapse',)
    })
  )
  
  readonly_fields = [
    'contract_number', 'created_by', 'created_at', 'updated_by', 'updated_at',
    'approved_by', 'approved_at'
  ]
  
  def status_badge(self, obj):
    colors = {
      'draft': '#6c757d', 'approved': '#0dcaf0', 'active': '#198754',
      'completed': '#0d6efd', 'cancelled': '#dc3545'
    }
    return format_html(
      f'<span style="background: {colors.get(obj.status)}; color: white; '
      f'padding: 3px 8px; border-radius: 3px;">{obj.get_status_display()}</span>'
    )
  status_badge.short_description = 'Status'
  
  def approval_status(self, obj):
    if obj.status == 'approved':
      return format_html('✅ Approved by {} on {}', obj.approved_by, obj.approved_at.strftime('%Y-%m-%d'))
    return "Pending Approval"
  approval_status.short_description = 'Approval'
  
  def revenue_status(self, obj):
    unrecognized = obj.get_unrecognized_revenue()
    recognized = obj.get_recognized_revenue()
    return f"Recognized: ${recognized} | Pending: ${unrecognized}"
  revenue_status.short_description = 'Revenue'
  
  actions = ['approve_contracts', 'mark_completed', 'mark_cancelled']
  
  def approve_contracts(self, request, queryset):
    updated = queryset.filter(status='draft').update(
      status='approved',
      approved_by=request.user,
      approved_at=timezone.now()
    )
    self.message_user(request, f'{updated} contracts approved')
  approve_contracts.short_description = 'Approve selected contracts'
```

**Implementation Priority:** MEDIUM  
**Effort:** 2-3 hours  
**Impact:** Professional dashboard, easier management, clear status

---

## 🔧 REFINEMENT 10: TESTING & VALIDATION SUITE

### Current State → Enhanced State

**Create Test Cases:**

```python
# tests/test_contract_revenue.py

class ContractRevenueRecognitionTests(TestCase):
  def test_direct_sale_revenue_immediate(self):
    """Direct sales recognize revenue at invoice"""
    sale = Sale.objects.create(sale_type='direct', amount=1000)
    invoice = Invoice.objects.create(sale=sale, amount=1000)
    
    ContractRevenueService.recognize_revenue(invoice)
    
    self.assertEqual(invoice.revenue_recognized, True)
    # Check GL entry exists
  
  def test_rental_revenue_deferred(self):
    """Rental deposits are liabilities"""
    contract = Contract.objects.create(type='rental', amount=100)
    invoice = Invoice.objects.create(contract=contract, invoice_type='deposit', amount=100)
    
    # Should create liability entry, not revenue
    entries = JournalEntry.objects.filter(invoice=invoice)
    # Verify: Debit Cash, Credit Unearned Revenue
  
  def test_custom_sale_final_only(self):
    """Custom sale revenue only on final invoice"""
    contract = Contract.objects.create(type='custom_sale', amount=1000)
    
    # Deposit invoice should NOT recognize revenue
    deposit = Invoice.objects.create(contract=contract, invoice_type='deposit', amount=200)
    self.assertFalse(ContractRevenueService.recognize_revenue_for_invoice(deposit))
    
    # Final invoice SHOULD recognize revenue
    final = Invoice.objects.create(contract=contract, invoice_type='final', amount=800)
    self.assertTrue(ContractRevenueService.recognize_revenue_for_invoice(final))

# tests/test_inventory_movement.py

class InventoryMovementTests(TestCase):
  def test_stock_reservation_for_rental(self):
    """Renting a product reserves stock"""
    product = Product.objects.create(name='Dress', quantity_in_stock=5)
    contract = Contract.objects.create(type='rental', product=product)
    
    InventoryService.reserve_stock(product, 1, contract)
    
    self.assertEqual(product.quantity_reserved, 1)
    self.assertEqual(product.quantity_in_stock, 5)  # Not reduced
  
  def test_cannot_reserve_more_than_available(self):
    """Cannot reserve stock that doesn't exist"""
    product = Product.objects.create(name='Dress', quantity_in_stock=5)
    contract = Contract.objects.create(type='rental', product=product)
    
    with self.assertRaises(InventoryError):
      InventoryService.reserve_stock(product, 10, contract)
  
  def test_stock_movement_immutable(self):
    """Stock movements cannot be edited"""
    movement = StockMovement.objects.create(
      product=Product.objects.create(name='Dress'),
      movement_type='sale',
      quantity_changed=-1,
      reference_id=1,
      reference_type='sale'
    )
    
    with self.assertRaises(PermissionDenied):
      movement.quantity_changed = -2
      movement.save()

# tests/test_gl_integrity.py

class GLIntegrityTests(TestCase):
  def test_journal_entry_balanced(self):
    """All GL entries must balance"""
    entry = JournalEntry.objects.create(
      entry_date=date.today(),
      entry_type='invoice'
    )
    
    JournalEntryLine.objects.create(entry=entry, account_id=1, debit=500)
    JournalEntryLine.objects.create(entry=entry, account_id=2, credit=500)
    
    self.assertTrue(entry.is_balanced())
  
  def test_unbalanced_entry_rejected(self):
    """Cannot post unbalanced entry"""
    entry = JournalEntry.objects.create(
      entry_date=date.today(),
      entry_type='invoice'
    )
    
    JournalEntryLine.objects.create(entry=entry, account_id=1, debit=500)
    JournalEntryLine.objects.create(entry=entry, account_id=2, credit=400)
    
    with self.assertRaises(GLError):
      entry.post()
```

**Implementation Priority:** HIGH  
**Effort:** 4-5 hours  
**Impact:** Ensures correctness, catches regressions, builds confidence

---

## 📊 HARDENING SUMMARY

| Refinement | Priority | Effort | Impact |
|-----------|----------|--------|--------|
| Contract Model | HIGH | 2-3h | Rules-driven |
| Invoice Model | HIGH | 2-3h | Revenue recognition |
| Inventory Model | HIGH | 3-4h | Audit trail |
| GL Posting | CRITICAL | 2-3h | Traceability |
| Service Layer | CRITICAL | 4-5h | Logic centralization |
| Audit Trail | MEDIUM | 1-2h | Complete history |
| Error Handling | HIGH | 2-3h | Reliability |
| API Hardening | HIGH | 2-3h | Data integrity |
| Admin UI | MEDIUM | 2-3h | Professionalism |
| Testing | HIGH | 4-5h | Confidence |

**Total Effort:** 24-32 hours  
**Impact:** Production-ready system

---

## ✅ POST-HARDENING CHECKLIST

- [ ] All models add created_by/updated_by audit fields
- [ ] All models implement validation in clean() method
- [ ] All services use try/except with proper error types
- [ ] All views validate contracts before creating transactions
- [ ] All admin interfaces show business status clearly
- [ ] All GL entries balanced and posted atomically
- [ ] All tests pass (100+ test cases)
- [ ] System check: 0 errors, 0 warnings
- [ ] Performance tested (< 100ms for list views)
- [ ] Audit trail verified for all changes

---

## 🚀 HARDENED SYSTEM READINESS

After these refinements:
- ✅ System is contract-centric (enforced at model level)
- ✅ Accounting is rule-based (every transaction double-entry)
- ✅ Inventory is immutable (audit trail complete)
- ✅ Revenue recognition is deferred (per contract type)
- ✅ Errors are prevented (not warned about)
- ✅ Complete traceability (who, what, when, why)

**Next Steps:** Phase 4 - Advanced Reporting & Reconciliation

This establishes the hard foundation for all subsequent features.
