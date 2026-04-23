# SYSTEM HARDENING IMMEDIATE ACTION PLAN
## Critical Refinements to Phases 1-3 (Begin Now)

**Objective:** Elevate existing implementation to production-grade  
**Scope:** 10 critical refinements across models, services, validation, error handling  
**Timeline:** 24-32 hours total effort  
**Priority:** HIGH - Required before Phase 4 launch  

---

## REFINEMENT 1: Contract Model Enhancements
**Priority:** CRITICAL | Effort:** 2-3 hours | **Impact:** High

### Current State
```python
# Current crm/models.py
class Contract(models.Model):
    contract_number = models.CharField(...)  # Auto-numbered
    type = models.CharField(...)  # rental, custom_sale, custom_rent
    customer = models.ForeignKey(...)
    product = models.ForeignKey(...)
    rental_start_date = models.DateField()
    rental_end_date = models.DateField()
    status = models.CharField(...)  # draft, approved, active, completed
    security_deposit = models.DecimalField()
    payment_terms = models.CharField()
    late_return_penalty = models.DecimalField()  # ← New
    damage_clause_amount = models.DecimalField()  # ← New
    # Missing: design_specs, measurements, revenue_schedule
```

### Enhanced State
```python
# Enhanced crm/models.py
class Contract(models.Model):
    contract_number = models.CharField(max_length=20, unique=True)
    type = models.CharField(
        max_length=20,
        choices=[
            ('rental', 'Rental'),
            ('custom_sale', 'Custom-Made for Sale'),
            ('custom_rent', 'Custom-Made for Rent'),
            ('direct_sale', 'Direct Sale (no contract)')
        ]
    )
    
    # Party & Product
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    # Dates
    rental_start_date = models.DateField(null=True, blank=True)
    rental_end_date = models.DateField(null=True, blank=True)
    
    # Design & Specifications (Custom-made only)
    design_specs = models.JSONField(
        default=dict,
        help_text='{"fabric": "silk", "color": "navy", "style": "formal", ...}'
    )
    measurements = models.JSONField(
        default=dict,
        help_text='{"chest": "38", "waist": "32", "length": "42", ...}'
    )
    
    # Financial Terms
    contract_value = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_terms = models.CharField(max_length=100)
    
    # Penalties & Clauses
    late_return_penalty = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Daily charge for late return'
    )
    damage_clause_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Max liability for damage'
    )
    
    # Revenue Schedule (for deferred revenue)
    revenue_schedule = models.JSONField(
        default=dict,
        help_text='[{"date": "2026-02-01", "amount": 5000}, ...]'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ]
    )
    
    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contracts_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contracts_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status Tracking
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts_approved')
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Lock after first invoice (prevent modification)
    is_locked_for_invoicing = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.contract_number:
            self.contract_number = self.generate_contract_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_contract_number():
        import datetime
        today = datetime.date.today()
        count = Contract.objects.filter(
            created_at__date=today
        ).count() + 1
        return f"CONT-{today.strftime('%Y%m%d')}-{count:05d}"
    
    def can_invoice(self):
        """Check if contract can create invoice"""
        return self.status == 'approved'
    
    def can_reserve_stock(self):
        """Check if stock can be reserved"""
        return self.status == 'approved' and self.type in ['rental', 'custom_rent']
    
    def lock_after_first_invoice(self):
        """Lock contract after first invoice"""
        self.is_locked_for_invoicing = True
        self.save()
    
    def get_revenue_schedule(self):
        """Return revenue recognition schedule"""
        return self.revenue_schedule
    
    def get_unrecognized_revenue(self):
        """Calculate unrecognized deferred revenue"""
        # Sum of deposits not yet recognized
        pass
    
    def validate_rental_dates(self):
        """Prevent overlapping rental dates"""
        if self.type != 'rental':
            return True
        
        from django.db.models import Q
        overlapping = Contract.objects.filter(
            product=self.product,
            type='rental',
            status='active',
            rental_start_date__lt=self.rental_end_date,
            rental_end_date__gt=self.rental_start_date
        ).exclude(pk=self.pk)
        
        return not overlapping.exists()
    
    def __str__(self):
        return f"{self.contract_number} - {self.customer.name}"
```

### Action Items
1. [ ] Add JSONField imports: `from django.db.models import JSONField`
2. [ ] Add new fields: `design_specs`, `measurements`, `revenue_schedule`, `approved_at`, `approved_by`, `completed_at`, `is_locked_for_invoicing`, `updated_by`
3. [ ] Update `created_by` field (add to existing)
4. [ ] Add validation methods: `can_invoice()`, `can_reserve_stock()`, `validate_rental_dates()`, `get_revenue_schedule()`
5. [ ] Create migration: `python manage.py makemigrations crm`
6. [ ] Apply migration: `python manage.py migrate crm`

---

## REFINEMENT 2: Invoice Model Revenue Recognition
**Priority:** CRITICAL | **Effort:** 2-3 hours | **Impact:** High

### Current State (Phase 2)
```python
# Current sales/models.py
class Invoice(models.Model):
    contract = models.ForeignKey(Contract, ...)
    invoice_type = models.CharField(...)  # standard, deposit, interim, final
    amount = models.DecimalField()
    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True)
    posted_by = models.ForeignKey(User, ...)
    # Missing: revenue recognition tracking
```

### Enhanced State
```python
# Enhanced sales/models.py
class Invoice(models.Model):
    # Existing fields
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT)
    invoice_number = models.CharField(max_length=20, unique=True)
    invoice_type = models.CharField(
        max_length=20,
        choices=[
            ('standard', 'Standard Sale'),
            ('deposit', 'Deposit'),
            ('interim', 'Interim Payment'),
            ('final', 'Final Settlement')
        ]
    )
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # GL Posting
    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='invoices_posted'
    )
    
    # ← NEW: Revenue Recognition
    revenue_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        null=True, blank=True,
        limit_choices_to={'account_type': 'income'},
        help_text='GL account for revenue (e.g., Sales Revenue, Rental Revenue)'
    )
    
    revenue_recognized = models.BooleanField(default=False)
    recognized_at = models.DateTimeField(null=True, blank=True)
    recognized_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='invoices_revenue_recognized'
    )
    
    # Invoice Classification
    deposit_invoice = models.BooleanField(default=False)  # Is this a deposit?
    final_invoice = models.BooleanField(default=False)   # Is this final for contract?
    
    # Audit
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='invoices_created'
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='invoices_updated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status (derived from payments)
    def get_status(self):
        total_paid = Payment.objects.filter(invoice=self).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        if total_paid == 0:
            return 'unpaid'
        elif total_paid < self.amount:
            return 'partial'
        else:
            return 'paid'
    
    def can_recognize_revenue(self):
        """Check if revenue can be recognized"""
        if self.revenue_recognized:
            return False
        
        if self.invoice_type == 'deposit':
            return False  # Deposits are liabilities
        
        if self.contract.type == 'custom_sale':
            return self.final_invoice  # Only recognize on final
        
        if self.contract.type == 'rental':
            return self.final_invoice  # Only recognize on final
        
        return True  # Standard & direct sales recognize immediately
    
    def recognize_revenue(self, user):
        """Recognize revenue with GL posting"""
        if not self.can_recognize_revenue():
            raise ValueError("Revenue cannot be recognized for this invoice")
        
        if not self.revenue_account:
            raise ValueError("Revenue account not configured")
        
        # Create GL entry
        from financeaccounting.services import GLService
        gl_service = GLService()
        
        # Debit AR, Credit Revenue
        gl_service.create_journal_entry(
            date=self.invoice_date,
            description=f"Revenue recognition - {self.invoice_number}",
            lines=[
                {
                    'account': self.get_ar_account(),
                    'debit': self.amount,
                    'credit': 0
                },
                {
                    'account': self.revenue_account,
                    'debit': 0,
                    'credit': self.amount
                }
            ],
            source_type='invoice',
            source_id=self.id
        )
        
        self.revenue_recognized = True
        self.recognized_at = now()
        self.recognized_by = user
        self.save()
    
    def check_revenue_recognition_rules(self):
        """Validate revenue recognition business rules"""
        rules = []
        
        if self.invoice_type == 'deposit':
            rules.append("Deposits are liabilities, not revenue")
        
        if self.contract.type in ['custom_sale', 'custom_rent']:
            if not self.final_invoice:
                rules.append(f"Only final invoice triggers revenue for {self.contract.type}")
        
        return rules
    
    def get_unearned_portion(self):
        """Calculate unearned revenue for balance sheet"""
        if self.invoice_type != 'deposit':
            return 0
        return self.amount
    
    def __str__(self):
        return f"{self.invoice_number} - {self.contract.customer.name}"
```

### Action Items
1. [ ] Add fields: `revenue_account` (FK), `revenue_recognized`, `recognized_at`, `recognized_by`, `deposit_invoice`, `final_invoice`, `created_by`, `updated_by`
2. [ ] Add methods: `can_recognize_revenue()`, `recognize_revenue(user)`, `check_revenue_recognition_rules()`, `get_unearned_portion()`
3. [ ] Update `get_status()` method to derive from payments
4. [ ] Create migration
5. [ ] Apply migration

---

## REFINEMENT 3: Inventory - StockMovement Immutable Audit Trail
**Priority:** CRITICAL | **Effort:** 3-4 hours | **Impact:** Critical

### Current State
```python
# Current inventory/models.py
class Product(models.Model):
    name = models.CharField()
    quantity_in_stock = models.IntegerField()
    # ← Problem: Direct edits, no audit trail
```

### Enhanced State
```python
# Enhanced inventory/models.py

class StockMovement(models.Model):
    """Immutable audit trail of all stock movements"""
    
    # Movement Type
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase from Supplier'),
        ('sale', 'Sale to Customer'),
        ('reserve', 'Reserved for Rental'),
        ('release', 'Released from Reservation'),
        ('production', 'Custom Production Completed'),
        ('return', 'Return from Customer'),
        ('adjustment', 'Inventory Adjustment'),
    ]
    
    # Core Fields
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity_changed = models.IntegerField()  # Signed (+ or -)
    
    # Snapshots (immutable)
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    
    # Reference (audit trail)
    reference_type = models.CharField(
        max_length=20,
        choices=[
            ('contract', 'Contract'),
            ('sale', 'Sale'),
            ('invoice', 'Invoice'),
            ('expense', 'Expense'),
            ('adjustment', 'Adjustment'),
        ]
    )
    reference_id = models.IntegerField()  # ID of contract/sale/etc
    reference_number = models.CharField(max_length=50)  # CONT-123, SAL-456, etc
    
    # Timing & User
    movement_date = models.DateField(auto_now_add=True)
    movement_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Immutability
    is_reversal = models.BooleanField(default=False)
    reversal_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reversals'
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps (immutable after creation)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Prevent editing or deletion
        permissions = [
            ('can_reverse_stock_movement', 'Can reverse stock movement'),
        ]
        indexes = [
            models.Index(fields=['product', 'movement_date']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]
    
    def save(self, *args, **kwargs):
        # First save - calculate snapshots
        if not self.pk:
            self.quantity_before = self.product.quantity_in_stock
            self.quantity_after = self.quantity_before + self.quantity_changed
            
            # Validation: prevent negative stock
            if self.quantity_after < 0:
                raise ValueError(
                    f"Cannot create movement: Would result in negative stock. "
                    f"Before: {self.quantity_before}, Change: {self.quantity_changed}"
                )
            
            # Update product stock
            self.product.quantity_in_stock = self.quantity_after
            self.product.save()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # PREVENT deletion - this is immutable audit trail
        raise PermissionError("StockMovement records cannot be deleted. Create reversal instead.")
    
    def reverse(self, reason, created_by):
        """Create offset reversal instead of deletion"""
        reversal = StockMovement(
            product=self.product,
            movement_type=self.movement_type,
            quantity_changed=-self.quantity_changed,  # Negative of original
            reference_type=self.reference_type,
            reference_id=self.reference_id,
            reference_number=self.reference_number,
            is_reversal=True,
            reversal_of=self,
            notes=f"Reversal of {self.reference_number}: {reason}",
            created_by=created_by
        )
        reversal.save()
        return reversal
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity_changed:+d})"

# Update Product model
class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    # Never edit directly - use StockMovement
    quantity_in_stock = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)  # For rentals
    quantity_on_order = models.IntegerField(default=0)
    
    # Financials
    cost_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    selling_price = models.DecimalField(max_digits=8, decimal_places=2)
    rental_price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Product Type
    PRODUCT_TYPE_CHOICES = [
        ('standard', 'Standard Product'),
        ('rental', 'Rental Item'),
        ('custom', 'Custom-Made'),
        ('package', 'Package/Bundle'),
    ]
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    
    # Inventory Policy
    reorder_level = models.IntegerField(default=0)
    reorder_quantity = models.IntegerField(default=0)
    
    def get_available_quantity(self):
        """Available for sale = in_stock - reserved"""
        return self.quantity_in_stock - self.quantity_reserved
    
    def get_inventory_value(self):
        """Total value at cost"""
        return self.quantity_in_stock * self.cost_per_unit
    
    def is_low_stock(self):
        """Check if below reorder level"""
        return self.quantity_in_stock <= self.reorder_level
    
    def __str__(self):
        return f"{self.name} ({self.sku}) - {self.quantity_in_stock} in stock"
```

### Action Items
1. [ ] Create StockMovement model
2. [ ] Add methods: `reverse()`, `get_available_quantity()`, `get_inventory_value()`, `is_low_stock()`
3. [ ] Update Product model with cost tracking
4. [ ] Create migration: `python manage.py makemigrations inventory`
5. [ ] Apply migration
6. [ ] Create management command to audit existing stock (optional)

---

## REFINEMENT 4: GL Posting - RevenueRecognitionLog & Integrity
**Priority:** CRITICAL | **Effort:** 2-3 hours | **Impact:** Critical

### New Model: RevenueRecognitionLog
```python
# financeaccounting/models.py

class RevenueRecognitionLog(models.Model):
    """Track all revenue recognition events for GL integrity"""
    
    TRANSACTION_TYPES = [
        ('deposit_received', 'Deposit Received'),
        ('revenue_recognized', 'Revenue Recognized'),
        ('revenue_reversed', 'Revenue Reversed'),
        ('invoice_finalized', 'Invoice Finalized'),
    ]
    
    # Reference
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, null=True, blank=True)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    
    # GL Impact
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    account_debited = models.ForeignKey(
        'ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='revenue_log_debits'
    )
    account_credited = models.ForeignKey(
        'ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='revenue_log_credits'
    )
    
    # Journal Entry Link
    journal_entry = models.ForeignKey(
        'JournalEntry',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    # Audit
    recognized_date = models.DateField()
    recognized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.contract.contract_number} - {self.get_transaction_type_display()}"


class GLIntegrityCheck(models.Model):
    """Daily GL integrity verification"""
    
    check_date = models.DateField(auto_now_add=True)
    total_debits = models.DecimalField(max_digits=15, decimal_places=2)
    total_credits = models.DecimalField(max_digits=15, decimal_places=2)
    is_balanced = models.BooleanField()
    discrepancy = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-check_date']
```

### Enhanced GLService
```python
# financeaccounting/services.py

class GLIntegrityService:
    """Verify GL always balanced"""
    
    @staticmethod
    def verify_balance():
        """Check if all journal entries balance"""
        from accounting.models import JournalEntry, JournalEntryLine
        
        entries = JournalEntry.objects.all()
        issues = []
        
        for entry in entries:
            lines = JournalEntryLine.objects.filter(journal_entry=entry)
            debits = sum(line.debit_amount for line in lines)
            credits = sum(line.credit_amount for line in lines)
            
            if debits != credits:
                issues.append({
                    'entry_id': entry.id,
                    'reference': entry.reference,
                    'debits': debits,
                    'credits': credits,
                    'discrepancy': debits - credits
                })
        
        return issues
    
    @staticmethod
    def daily_reconciliation(user):
        """Run daily GL reconciliation"""
        from accounting.models import JournalEntry, JournalEntryLine, GLIntegrityCheck
        
        lines = JournalEntryLine.objects.filter(is_posted=True)
        total_debits = sum(line.debit_amount for line in lines)
        total_credits = sum(line.credit_amount for line in lines)
        
        is_balanced = abs(total_debits - total_credits) < 0.01  # Allow rounding
        
        check = GLIntegrityCheck(
            total_debits=total_debits,
            total_credits=total_credits,
            is_balanced=is_balanced,
            discrepancy=total_debits - total_credits,
            performed_by=user
        )
        check.save()
        
        return check
```

### Action Items
1. [ ] Create RevenueRecognitionLog model
2. [ ] Create GLIntegrityCheck model
3. [ ] Create GLIntegrityService
4. [ ] Add daily reconciliation task (celery or scheduled)
5. [ ] Create migration

---

## REFINEMENT 5: Service Layer Completion
**Priority:** CRITICAL | **Effort:** 4-5 hours | **Impact:** High

### New Services to Implement

```python
# financeaccounting/services.py

class ContractRevenueService:
    """Manage revenue recognition per contract"""
    
    @staticmethod
    def calculate_revenue_recognition_schedule(contract):
        """Generate revenue schedule for custom contracts"""
        if contract.type == 'custom_sale':
            # Custom sale: 50% on signing, 50% on completion
            return [
                {'date': contract.created_at, 'amount': contract.contract_value * 0.5, 'type': 'deposit'},
                {'date': contract.estimated_completion, 'amount': contract.contract_value * 0.5, 'type': 'final'},
            ]
        elif contract.type == 'custom_rent':
            # Custom rent: deposit upfront, rental revenue per terms
            return [
                {'date': contract.rental_start_date, 'amount': contract.security_deposit, 'type': 'deposit'},
                {'date': contract.rental_start_date, 'amount': contract.monthly_rental, 'type': 'monthly'},
            ]
        else:
            return []
    
    @staticmethod
    def recognize_revenue_for_invoice(invoice, user):
        """Recognize revenue when conditions met"""
        if not invoice.can_recognize_revenue():
            raise ValueError("Revenue cannot be recognized yet")
        
        invoice.recognize_revenue(user)


class InventoryService:
    """Manage all inventory operations"""
    
    @staticmethod
    def reserve_stock(product, quantity, contract, created_by):
        """Reserve stock for rental contract"""
        movement = StockMovement(
            product=product,
            movement_type='reserve',
            quantity_changed=-quantity,
            reference_type='contract',
            reference_id=contract.id,
            reference_number=contract.contract_number,
            created_by=created_by,
            notes=f"Reserved for {contract.contract_number}"
        )
        movement.save()
        return movement
    
    @staticmethod
    def release_stock(product, quantity, contract, reason, created_by):
        """Release reserved stock"""
        movement = StockMovement(
            product=product,
            movement_type='release',
            quantity_changed=quantity,
            reference_type='contract',
            reference_id=contract.id,
            reference_number=contract.contract_number,
            created_by=created_by,
            notes=f"Released from {contract.contract_number}: {reason}"
        )
        movement.save()
        return movement
    
    @staticmethod
    def record_sale(product, quantity, sale, created_by):
        """Record sale stock movement"""
        movement = StockMovement(
            product=product,
            movement_type='sale',
            quantity_changed=-quantity,
            reference_type='sale',
            reference_id=sale.id,
            reference_number=sale.sale_number,
            created_by=created_by
        )
        movement.save()
        return movement


class ContractValidationService:
    """Validate contract business rules"""
    
    @staticmethod
    def validate_contract_before_approval(contract):
        """Check all rules before approval"""
        errors = []
        
        # Required fields
        if not contract.customer:
            errors.append("Customer is required")
        if not contract.product:
            errors.append("Product is required")
        
        # Type-specific validation
        if contract.type in ['rental', 'custom_rent']:
            if not contract.rental_start_date or not contract.rental_end_date:
                errors.append("Rental dates required")
            if contract.rental_end_date <= contract.rental_start_date:
                errors.append("End date must be after start date")
            if contract.security_deposit <= 0:
                errors.append("Security deposit required for rentals")
        
        if contract.type in ['custom_sale', 'custom_rent']:
            if not contract.design_specs:
                errors.append("Design specifications required for custom items")
            if not contract.measurements:
                errors.append("Measurements required for custom items")
        
        # Check rental date conflicts
        if contract.type == 'rental':
            if not contract.validate_rental_dates():
                errors.append("Rental dates conflict with existing rental")
        
        return errors
```

### Action Items
1. [ ] Create ContractRevenueService
2. [ ] Create InventoryService
3. [ ] Create ContractValidationService
4. [ ] Create GLService (if not exists)
5. [ ] Create ReportService
6. [ ] Add unit tests for all services

---

## REFINEMENT 6: Audit Trail Completeness
**Priority:** MEDIUM | **Effort:** 1-2 hours | **Impact:** Medium

### Ensure All Models Have Audit Fields

```python
# All models must have:
created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

### Models to Update
- [ ] Contract (✓ already has)
- [ ] Invoice (✓ already has in Phase 2)
- [ ] Expense (✓ already has in Phase 3)
- [ ] Product (add)
- [ ] Customer (add)
- [ ] Sale (add)
- [ ] Payment (add)
- [ ] JournalEntry (verify)
- [ ] ChartOfAccounts (add)

---

## REFINEMENT 7: Error Handling Hierarchy
**Priority:** HIGH | **Effort:** 2-3 hours | **Impact:** Medium

```python
# core/exceptions.py

class RimanERPException(Exception):
    """Base exception for all ERP errors"""
    pass

class ContractException(RimanERPException):
    """Contract-related errors"""
    pass

class ContractLocked(ContractException):
    """Contract cannot be modified"""
    pass

class InventoryException(RimanERPException):
    """Inventory-related errors"""
    pass

class NegativeStockException(InventoryException):
    """Cannot create negative stock"""
    pass

class InsufficientStockException(InventoryException):
    """Stock not available"""
    pass

class RevenueRecognitionException(RimanERPException):
    """Revenue recognition errors"""
    pass

class GLException(RimanERPException):
    """GL integrity errors"""
    pass

class GLMismatchException(GLException):
    """Debits do not equal credits"""
    pass

class PaymentException(RimanERPException):
    """Payment processing errors"""
    pass

class ValidationException(RimanERPException):
    """Business rule validation errors"""
    pass
```

### Action Items
1. [ ] Create core/exceptions.py
2. [ ] Update all services to raise custom exceptions
3. [ ] Update views to catch and handle exceptions
4. [ ] Add logging for all exceptions

---

## REFINEMENT 8: API Hardening
**Priority:** HIGH | **Effort:** 2-3 hours | **Impact:** Medium

### Add Validation to All Views

```python
# Example in accounting/views.py

class ExpenseCreateView(CreateView):
    def post(self, request, *args, **kwargs):
        # Validate user
        if not request.user.is_authenticated:
            raise ValidationException("User not authenticated")
        
        # Validate form data
        form = ExpenseForm(request.POST, request.FILES)
        if not form.is_valid():
            raise ValidationException(f"Invalid form: {form.errors}")
        
        # Validate business rules
        amount = form.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationException("Expense amount must be positive")
        
        # Create with audit fields
        expense = form.save(commit=False)
        expense.created_by = request.user
        expense.save()
        
        return redirect('accounting:expense-detail', pk=expense.pk)
```

### Action Items
1. [ ] Add validation to all views
2. [ ] Add exception handling middleware
3. [ ] Add logging for all API calls
4. [ ] Add rate limiting (optional)

---

## REFINEMENT 9: Admin UI Professionalization
**Priority:** MEDIUM | **Effort:** 2-3 hours | **Impact:** Medium

### Example: Enhanced Admin Interface

```python
# accounting/admin.py

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_number', 'expense_date', 'expense_type_badge', 'amount', 'status_badge', 'submitted_by', 'approved_by')
    list_filter = ('status', 'expense_type', 'expense_date', 'is_posted')
    search_fields = ('expense_number', 'description', 'supplier__name')
    readonly_fields = ('expense_number', 'created_at', 'updated_at', 'created_by', 'updated_by', 'posted_at', 'posted_by', 'submitted_at', 'submitted_by', 'approved_at', 'approved_by')
    
    fieldsets = (
        ('Expense Number', {
            'fields': ('expense_number',)
        }),
        ('Details', {
            'fields': ('expense_date', 'expense_type', 'description', 'amount', 'account', 'supplier', 'reference_number', 'receipt_file')
        }),
        ('Workflow', {
            'fields': ('status', 'notes')
        }),
        ('Approval', {
            'fields': ('submitted_at', 'submitted_by', 'approved_at', 'approved_by'),
            'classes': ('collapse',)
        }),
        ('GL Posting', {
            'fields': ('is_posted', 'posted_at', 'posted_by'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_expenses', 'reject_expenses', 'post_to_gl']
    
    def expense_type_badge(self, obj):
        colors = {
            'office_supplies': 'blue',
            'labor': 'green',
            'utilities': 'orange',
            'rent': 'red',
            'marketing': 'purple',
            'transportation': 'teal',
            'maintenance': 'gray',
            'salaries': 'darkblue',
            'other': 'black',
        }
        color = colors.get(obj.expense_type, 'black')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_expense_type_display()
        )
    expense_type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        colors = {
            'draft': '#999999',
            'submitted': '#0066CC',
            'approved': '#00CC66',
            'posted': '#009933',
            'rejected': '#FF0000',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_expenses(self, request, queryset):
        for expense in queryset:
            if expense.can_approve():
                expense.status = 'approved'
                expense.approved_at = now()
                expense.approved_by = request.user
                expense.save()
        self.message_user(request, f"{queryset.count()} expenses approved")
    approve_expenses.short_description = "Approve selected expenses"
    
    def reject_expenses(self, request, queryset):
        for expense in queryset:
            if expense.can_approve():
                expense.status = 'rejected'
                expense.save()
        self.message_user(request, f"{queryset.count()} expenses rejected")
    reject_expenses.short_description = "Reject selected expenses"
    
    def post_to_gl(self, request, queryset):
        for expense in queryset:
            if expense.status == 'approved' and not expense.is_posted:
                expense.post_to_gl(request.user)
                expense.is_posted = True
                expense.posted_at = now()
                expense.posted_by = request.user
                expense.save()
        self.message_user(request, f"{queryset.count()} expenses posted to GL")
    post_to_gl.short_description = "Post selected expenses to GL"
```

### Action Items
1. [ ] Add fieldsets to all admin classes
2. [ ] Add color-coded badges
3. [ ] Add bulk actions
4. [ ] Add filtering & search
5. [ ] Add readonly fields

---

## REFINEMENT 10: Testing Suite (100+ Test Cases)
**Priority:** HIGH | **Effort:** 4-5 hours | **Impact:** High

### Create Test Files

```python
# accounting/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class ContractRevenueTestCase(TestCase):
    """Test revenue recognition business rules"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.customer = Customer.objects.create(name='Test Customer')
        self.product = Product.objects.create(name='Test Product', sku='TEST1', cost_per_unit=100)
    
    def test_direct_sale_recognizes_revenue_immediately(self):
        """Direct sale revenue recognized at invoice"""
        # Create sale
        # Create invoice
        # Check GL entry created with revenue recognized
        pass
    
    def test_rental_defers_revenue_on_deposit(self):
        """Rental deposit recorded as liability"""
        # Create rental contract
        # Create deposit invoice
        # Check GL: Debit Cash, Credit Unearned Revenue (liability)
        pass
    
    def test_custom_sale_defers_all_revenue(self):
        """Custom sale only recognizes on final invoice"""
        # Create custom contract
        # Create deposit invoice
        # Check GL: no revenue recognized
        # Create final invoice
        # Check GL: all revenue recognized
        pass
    
    # ... 97 more test cases

class InventoryTestCase(TestCase):
    """Test inventory audit trail"""
    
    def test_stock_movement_prevents_negative_inventory(self):
        """Cannot create movement resulting in negative stock"""
        product = Product.objects.create(name='Test', sku='TEST1', quantity_in_stock=10)
        
        with self.assertRaises(ValueError):
            StockMovement.objects.create(
                product=product,
                movement_type='sale',
                quantity_changed=-20  # More than available
            )
    
    def test_stock_movement_immutable(self):
        """Cannot delete stock movements"""
        product = Product.objects.create(name='Test', sku='TEST1', quantity_in_stock=100)
        movement = StockMovement.objects.create(
            product=product,
            movement_type='sale',
            quantity_changed=-10
        )
        
        with self.assertRaises(PermissionError):
            movement.delete()
    
    # ... more test cases

class GLIntegrityTestCase(TestCase):
    """Test GL always balanced"""
    
    def test_gl_always_balanced(self):
        """Every posting must have debits = credits"""
        # Create various transactions
        # Check GL integrity
        pass
```

### Action Items
1. [ ] Create accounting/tests.py (30+ contract tests)
2. [ ] Create inventory/tests.py (30+ inventory tests)
3. [ ] Create financeaccounting/tests.py (30+ GL tests)
4. [ ] Create sales/tests.py (20+ invoice tests)
5. [ ] Run tests: `python manage.py test`
6. [ ] Achieve 80%+ coverage

---

## 🚀 HARDENING EXECUTION PLAN

### Week 1: Complete Refinements
- [ ] **Day 1**: Refinement 1 (Contract Model) + Refinement 2 (Invoice Revenue)
- [ ] **Day 2**: Refinement 3 (StockMovement) + Refinement 4 (GL Integrity)
- [ ] **Day 3**: Refinement 5 (Services) + Refinement 6 (Audit Trail)
- [ ] **Day 4**: Refinement 7 (Error Handling) + Refinement 8 (API Hardening)
- [ ] **Day 5**: Refinement 9 (Admin UI) + Refinement 10 (Testing)

### System Check After Hardening
```bash
python manage.py check
python manage.py test
python manage.py makemigrations
python manage.py migrate
```

### Expected Result
```
✅ 0 errors, 0 warnings
✅ 100+ test cases passing
✅ All migrations applied
✅ System ready for Phase 4
```

---

## ✨ HARDENING COMPLETE

After completing all 10 refinements:

✅ Contract model enterprise-grade  
✅ Revenue recognition rule-based  
✅ Inventory immutable audit trail  
✅ GL always balanced  
✅ Service layer complete  
✅ Audit trail comprehensive  
✅ Error handling professional  
✅ API hardened  
✅ Admin UI polished  
✅ 100+ tests passing  

**System ready for Phase 4: Advanced Reporting**

---

**Status:** 🟡 READY TO BEGIN  
**Next:** Phase 4 - Advanced Reporting & Reconciliation  
**Timeline:** 1 week to production-ready  

🚀 **LET'S HARDEN THIS SYSTEM**
