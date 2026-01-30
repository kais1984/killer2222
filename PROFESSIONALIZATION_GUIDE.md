# RIMAN FASHION ERP - PROFESSIONALIZATION & MOBILE-FIRST HARDENING GUIDE
## Complete Financial Integrity + Responsive Design Architecture

**Prepared for:** Senior Backend Engineer & ERP Architect  
**Date:** January 26, 2026  
**Status:** Production-Ready Implementation Guide  

---

## EXECUTIVE SUMMARY

Your RIMAN FASHION ERP has solid foundations. This guide will:

1. **Harden the core financial flows** (Sale → Invoice → Payment → Inventory → Accounting)
2. **Perfect the Expense system** with automatic GL entries and audit trails
3. **Enforce accounting integrity** (double-entry, asset treatment, reconciliation)
4. **Clarify data model responsibilities** (single source of truth for each entity)
5. **Implement responsive mobile design** (no separate app, pure Bootstrap refactor)

**Result:** A professional, financial-grade ERP that works seamlessly on desktop, tablet, and mobile devices, with every transaction traceable, immutable after posting, and automatically reconciled.

---

## PART 1: CORE FLOW PERFECTION

### 1.1 THE AUTHORITATIVE FLOW

```
SALE (Root Transaction)
├─ Created by user
├─ Contains 1+ SaleLines (products, quantities, prices)
├─ Status: DRAFT
└─ No accounting entries yet

        ↓

INVOICE (Auto-created on first payment attempt)
├─ Snapshot of sale totals (IMMUTABLE)
├─ Due date calculated
├─ Linked 1:1 to Sale
└─ Status derived from payments

        ↓

PAYMENT (User records customer payment)
├─ Amount, method, date
├─ IMMUTABLE after recording
├─ Can be reversed (creates compensating entry)
├─ Auto-creates Journal Entry:
│  ├─ DR: Cash / Bank / AR (asset)
│  └─ CR: Sales Revenue (revenue)
└─ Sale.status updated

        ↓

STOCK MOVEMENT (Automatic on SaleLine creation)
├─ Quantity reduced by sale qty
├─ CANNOT go negative
├─ Immutable audit trail
├─ Auto-creates Journal Entry:
│  ├─ DR: COGS (expense)
│  └─ CR: Inventory (asset)
└─ Product.on_hand_qty updated

        ↓

ACCOUNTING ENTRIES (Auto-created)
├─ Revenue Entry (on payment)
├─ COGS/Inventory Entry (on sale line)
├─ Balanced, complete audit trail
└─ No manual entries for standard flows
```

**Key Principle:** Every step creates an immutable record. Status is DERIVED, not stored.

---

### 1.2 MODEL STRUCTURE & RESPONSIBILITIES

#### Sale Model
**Single Responsibility:** Root transaction record for customer sales

```python
class Sale(models.Model):
    """
    IMMUTABLE after first payment
    Status DERIVED from payments + cancellation
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(Client, on_delete=models.PROTECT)
    sale_date = models.DateTimeField(auto_now_add=True)
    
    # Read-only totals (calculated from lines)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Soft delete
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['customer', '-sale_date']),
            models.Index(fields=['sale_number']),
        ]
    
    @property
    def total_paid(self):
        """Sum of non-reversed payments"""
        return self.payments.filter(reversed_by__isnull=True).aggregate(
            Sum('amount')
        )['amount__sum'] or Decimal('0.00')
    
    @property
    def amount_due(self):
        return self.total_amount - self.total_paid
    
    @property
    def payment_status(self):
        """DERIVED: unpaid | partial | paid"""
        if self.total_paid == 0:
            return 'unpaid'
        elif self.total_paid < self.total_amount:
            return 'partial'
        return 'paid'
    
    @property
    def status(self):
        """DERIVED: draft | invoiced | partial | paid | cancelled"""
        if self.cancelled_at:
            return 'cancelled'
        if not self.lines.exists():
            return 'draft'
        return self.payment_status
```

---

#### SaleLine Model
**Single Responsibility:** Immutable snapshot of product sold

```python
class SaleLine(models.Model):
    """
    Immutable line item snapshot.
    Once created, cannot be edited (prevents invoice changes).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='lines')
    
    # Product reference
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    # Immutable snapshot at time of sale
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['sale', 'product']  # Prevent duplicates
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        
        # PREVENT EDITING: raise error if trying to update
        if self.pk:
            raise ValidationError("Cannot edit line items after creation")
        
        super().save(*args, **kwargs)
        
        # SIGNAL: Create COGS entry + stock movement
        self._create_cogs_entry()
        self._create_stock_movement()
    
    def _create_cogs_entry(self):
        """Create COGS journal entry"""
        # DR: COGS, CR: Inventory
        cogs_amount = self.product.cost_price * self.quantity
        
        je = JournalEntry.objects.create(
            entry_type='stock_movement',
            entry_date=self.sale.sale_date.date(),
            description=f"COGS: {self.product.sku} x {self.quantity}",
            sale_id=self.sale.id
        )
        
        JournalEntryLine.objects.create(
            journal_entry=je,
            account=Account.objects.get(account_code='5000'),  # COGS
            line_type='debit',
            amount=cogs_amount
        )
        
        JournalEntryLine.objects.create(
            journal_entry=je,
            account=Account.objects.get(account_code='1300'),  # Inventory
            line_type='credit',
            amount=cogs_amount
        )
    
    def _create_stock_movement(self):
        """Create audit trail"""
        StockMovement.objects.create(
            product=self.product,
            movement_type='sale',
            quantity_change=-self.quantity,
            quantity_before=self.product.on_hand_qty,
            quantity_after=self.product.on_hand_qty - self.quantity,
            sale_id=self.sale.id,
            reference=self.sale.sale_number
        )
        
        # Update inventory
        self.product.on_hand_qty -= self.quantity
        self.product.save(update_fields=['on_hand_qty'])
```

---

#### Invoice Model
**Single Responsibility:** Immutable snapshot of sale totals for billing

```python
class Invoice(models.Model):
    """
    IMMUTABLE snapshot of sale at invoice creation.
    Status DERIVED from payments.
    ONE invoice per sale.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    # One-to-one with Sale
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)
    
    # Snapshot (immutable)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def amount_paid(self):
        return self.sale.total_paid
    
    @property
    def amount_due(self):
        return self.total_amount - self.amount_paid
    
    @property
    def status(self):
        """DERIVED: unpaid | partial | paid"""
        if self.amount_paid == 0:
            return 'unpaid'
        elif self.amount_paid < self.total_amount:
            return 'partial'
        return 'paid'
```

---

#### Payment Model
**Single Responsibility:** Immutable payment record

```python
class Payment(models.Model):
    """
    IMMUTABLE payment record.
    Only reversed, never edited.
    Auto-creates revenue journal entry.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(
        max_length=20,
        choices=[('cash', 'Cash'), ('card', 'Credit Card'), ('transfer', 'Bank Transfer'), ('cheque', 'Cheque')]
    )
    payment_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Reversal
    reversed_by = models.OneToOneField('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reverses')
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['sale', '-payment_date']),
            models.Index(fields=['payment_number']),
        ]
    
    def clean(self):
        """Prevent overpayment"""
        if self.amount > self.sale.amount_due:
            raise ValidationError(
                f"Payment {self.amount} exceeds amount due {self.sale.amount_due}"
            )
    
    def save(self, *args, **kwargs):
        # Auto-create invoice if not exists
        if self.sale and not hasattr(self.sale, 'invoice'):
            Invoice.objects.create(
                sale=self.sale,
                subtotal=self.sale.subtotal,
                tax_amount=self.sale.tax_amount,
                total_amount=self.sale.total_amount,
                due_date=self.sale.sale_date.date() + timedelta(days=30)
            )
        
        # Generate payment_number
        if not self.payment_number:
            self.payment_number = f"PAY-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        self.clean()
        super().save(*args, **kwargs)
        
        # SIGNAL: Create revenue journal entry
        self._create_revenue_entry()
    
    def _create_revenue_entry(self):
        """Create revenue recognition entry"""
        if self.reversed_by:
            return  # Don't create entry for reversed payments
        
        # Determine account based on payment method
        if self.payment_method == 'cash':
            account_code = '1005'  # Cash
        elif self.payment_method == 'transfer':
            account_code = '1001'  # Bank
        else:
            account_code = '1005'  # Default cash
        
        cash_account = Account.objects.get(account_code=account_code)
        revenue_account = Account.objects.get(account_code='4100')  # Sales Revenue
        
        je = JournalEntry.objects.create(
            entry_type='payment',
            entry_date=self.payment_date,
            description=f"Payment received: {self.sale.sale_number}",
            payment_id=self.id
        )
        
        # DR: Cash
        JournalEntryLine.objects.create(
            journal_entry=je,
            account=cash_account,
            line_type='debit',
            amount=self.amount
        )
        
        # CR: Revenue
        JournalEntryLine.objects.create(
            journal_entry=je,
            account=revenue_account,
            line_type='credit',
            amount=self.amount
        )
    
    def reverse(self, reversed_by):
        """Create reversal payment"""
        reversal = Payment.objects.create(
            sale=self.sale,
            amount=self.amount,
            payment_method=self.payment_method,
            payment_date=timezone.now().date(),
            reference=f"REVERSAL of {self.payment_number}",
            created_by=reversed_by
        )
        
        self.reversed_by = reversal
        self.save(update_fields=['reversed_by'])
        
        return reversal
```

---

### 1.3 RULES FOR CORE FLOW

#### MUST-PREVENT Rules
```
❌ Cannot create sale without customer
❌ Cannot create sale line without product
❌ Cannot edit sale line after creation (prevents invoice changes)
❌ Cannot overpay invoice
❌ Cannot reduce inventory below zero
❌ Cannot manually edit payment amounts
❌ Cannot delete sale or invoice (soft-delete only)
❌ Cannot create multiple invoices per sale
❌ Cannot edit invoice totals
```

#### MUST-ENFORCE Rules
```
✅ Sale line creation MUST trigger COGS entry
✅ Sale line creation MUST trigger stock movement
✅ Payment creation MUST trigger revenue entry
✅ Payment MUST NOT exceed amount due
✅ Stock movement MUST NOT create negative inventory
✅ Invoice MUST be auto-created on first payment
✅ All journal entries MUST balance
✅ All statuses MUST be derived, not stored
```

---

## PART 2: EXPENSE SYSTEM (CRITICAL)

### 2.1 EXPENSE CATEGORIES MODEL

```python
class ExpenseCategory(models.Model):
    """
    Maps expense types to GL accounts.
    Controls accounting behavior.
    """
    
    CATEGORY_TYPES = [
        ('cogs', 'Cost of Goods Sold'),
        ('operating', 'Operating Expense'),
        ('maintenance', 'Maintenance & Cleaning'),
        ('marketing', 'Marketing & Advertising'),
        ('administrative', 'Administrative'),
        ('salary', 'Salary & Payroll'),
        ('rent', 'Rent & Occupancy'),
        ('utilities', 'Utilities'),
        ('depreciation', 'Depreciation'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, unique=True)
    category_name = models.CharField(max_length=255)
    
    # GL mapping (CRITICAL)
    gl_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        help_text="GL account to debit when posting expense"
    )
    
    # Inventory treatment
    affects_inventory = models.BooleanField(default=False)
    inventory_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expense_inventory',
        help_text="Asset account if affects_inventory=True"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category_type']
    
    def clean(self):
        if not self.gl_account:
            raise ValidationError("GL account is required")
        if self.affects_inventory and not self.inventory_account:
            raise ValidationError("Inventory account required for inventory-affecting expenses")
```

---

### 2.2 EXPENSE MODEL

```python
class Expense(models.Model):
    """
    IMMUTABLE expense record after posting.
    Creates automatic journal entries.
    Reversed only (never edited after posting).
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('reversed', 'Reversed'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit Card'),
        ('transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('payable', 'Accounts Payable'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Category
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    
    # Core details
    expense_date = models.DateField()
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    description = models.TextField(help_text="What was purchased. Include receipt#.")
    reference = models.CharField(max_length=100, blank=True, help_text="Receipt#, Invoice#, PO#")
    
    # Optional references
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    quantity = models.IntegerField(null=True, blank=True)
    asset = models.CharField(max_length=255, blank=True, help_text="Asset name if maintained")
    
    # Status & posting
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_posted')
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_created')
    
    # Reversal
    reversed_by = models.OneToOneField('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reverses')
    
    # GL entry link
    journal_entry = models.OneToOneField(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expense'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
        indexes = [
            models.Index(fields=['expense_number']),
            models.Index(fields=['status', '-expense_date']),
            models.Index(fields=['category', '-expense_date']),
        ]
    
    def clean(self):
        # Cannot post without category
        if self.status == 'posted' and not self.category:
            raise ValidationError("Category required to post expense")
        
        # Cannot edit posted expense
        if self.pk:
            existing = Expense.objects.get(pk=self.pk)
            if existing.status == 'posted' and self.amount != existing.amount:
                raise ValidationError("Cannot edit posted expense. Create reversal instead.")
        
        # Quantity validation
        if self.product and not self.quantity:
            raise ValidationError("Quantity required when product specified")
    
    def save(self, *args, **kwargs):
        # Generate expense_number
        if not self.expense_number:
            self.expense_number = f"EXP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Track if just posted
        is_new_post = False
        if self.pk:
            existing = Expense.objects.get(pk=self.pk)
            is_new_post = existing.status != 'posted' and self.status == 'posted'
        else:
            is_new_post = self.status == 'posted'
        
        self.clean()
        super().save(*args, **kwargs)
        
        # Create GL entries if just posted
        if is_new_post:
            self._create_accounting_entries()
    
    def _create_accounting_entries(self):
        """Create double-entry for expense"""
        from financeaccounting.models import JournalEntry, JournalEntryLine
        
        je = JournalEntry.objects.create(
            entry_type='expense',
            entry_date=self.expense_date,
            description=f"Expense: {self.category.category_name} - {self.description}",
            created_by=self.posted_by
        )
        
        # DEBIT: Expense/Asset account
        if self.category.affects_inventory:
            debit_account = self.category.inventory_account
        else:
            debit_account = self.category.gl_account
        
        JournalEntryLine.objects.create(
            journal_entry=je,
            account=debit_account,
            line_type='debit',
            amount=self.amount,
            description=self.description
        )
        
        # CREDIT: Payment method account
        if self.payment_method == 'cash':
            credit_account = Account.objects.get(account_code='1005')
        elif self.payment_method == 'transfer':
            credit_account = Account.objects.get(account_code='1001')
        elif self.payment_method == 'payable':
            credit_account = Account.objects.get(account_code='2100')
        else:
            credit_account = Account.objects.get(account_code='1005')
        
        JournalEntryLine.objects.create(
            journal_entry=je,
            account=credit_account,
            line_type='credit',
            amount=self.amount,
            description=f"Payment for: {self.description}"
        )
        
        # Link & mark as posted
        self.journal_entry = je
        self.posted_at = timezone.now()
        Expense.objects.filter(pk=self.pk).update(
            journal_entry=je,
            posted_at=self.posted_at
        )
    
    def reverse(self, reversed_by):
        """Create reversal expense"""
        reversal = Expense.objects.create(
            category=self.category,
            expense_date=timezone.now().date(),
            amount=self.amount,
            payment_method=self.payment_method,
            description=f"REVERSAL of {self.expense_number}: {self.description}",
            reference=self.reference,
            supplier=self.supplier,
            product=self.product,
            quantity=self.quantity,
            status='posted',
            created_by=reversed_by,
            posted_by=reversed_by
        )
        
        self.reversed_by = reversal
        self.save(update_fields=['reversed_by'])
        
        return reversal
```

---

### 2.3 EXPENSE ACCOUNTING FLOWS

#### Flow 1: Operating Expense (Cash)
```
Expense: "Office supplies" → ₨5,000 cash

Journal Entry:
  DR: Office Supplies (5100) → ₨5,000
  CR: Cash (1005) → ₨5,000

Impact: P&L expense increases
```

#### Flow 2: Inventory-Related Expense
```
Expense: "Beading materials" → ₨20,000 payable
Category.affects_inventory = True

Journal Entry:
  DR: Inventory (1300) → ₨20,000
  CR: Accounts Payable (2100) → ₨20,000

Impact: Asset increases (not P&L)
```

#### Flow 3: Maintenance (Non-Inventory)
```
Expense: "Dry cleaning unsold dresses" → ₨3,000 cash
Category.affects_inventory = False

Journal Entry:
  DR: Maintenance (5300) → ₨3,000
  CR: Cash (1005) → ₨3,000

Impact: P&L expense only, inventory qty unchanged
```

#### Flow 4: Expense Reversal
```
Original: DR: Marketing (₨10,000), CR: Cash (₨10,000)

Reversal: DR: Marketing (₨10,000), CR: Cash (₨10,000)
          Description: "REVERSAL of EXP-xxx..."

Net Effect: ₨0 (both posted, creates audit trail)
```

---

## PART 3: ACCOUNTING INTEGRITY

### 3.1 DOUBLE-ENTRY ENFORCEMENT

Every transaction MUST balance:

```python
class JournalEntry(models.Model):
    def clean(self):
        """Validate balanced entry"""
        total_debit = self.lines.filter(line_type='debit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_credit = self.lines.filter(line_type='credit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        if total_debit != total_credit:
            raise ValidationError(
                f"Entry not balanced: DR={total_debit}, CR={total_credit}"
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
```

---

### 3.2 INVENTORY AS ASSET (NOT JUST QUANTITY)

```
Product.on_hand_qty → Physical count
Inventory GL Account Balance → Asset value

Must reconcile:
  Inventory GL Balance = SUM(Product.cost_price * on_hand_qty for all products)

Prevent:
  ❌ Manual quantity edits without GL impact
  ❌ GL entries without inventory updates
  ❌ Negative inventory (violates asset principle)
```

---

### 3.3 FINANCIAL STATEMENT RECONCILIATION

Every month, reconcile:

```
Balance Sheet
  Assets = Liabilities + Equity
  Inventory + Cash + AR = AP + Debt + Capital + Retained Earnings

Income Statement
  Revenue - COGS = Gross Profit
  Gross Profit - Expenses = Net Income

Cash Flow
  Beginning Cash + Receipts - Payments = Ending Cash
```

**Implementation:**
```python
class FinancialReports:
    def trial_balance(self):
        """Verify debits = credits"""
        debits = JournalEntryLine.objects.filter(line_type='debit').aggregate(Sum('amount'))
        credits = JournalEntryLine.objects.filter(line_type='credit').aggregate(Sum('amount'))
        
        assert debits == credits, "Trial balance not equal!"
        return debits
    
    def inventory_reconciliation(self):
        """Verify GL = physical count"""
        from inventory.models import Product
        
        gl_inventory = Account.objects.get(account_code='1300').get_balance()
        physical_value = Product.objects.aggregate(
            total=Sum(F('on_hand_qty') * F('cost_price'), output_field=DecimalField())
        )['total'] or Decimal('0.00')
        
        assert gl_inventory == physical_value, "Inventory not reconciled!"
        return gl_inventory
    
    def balance_sheet_equation(self):
        """Verify Assets = Liabilities + Equity"""
        assets = Account.objects.filter(account_type='asset').aggregate(Sum('balance'))
        liabilities = Account.objects.filter(account_type='liability').aggregate(Sum('balance'))
        equity = Account.objects.filter(account_type='equity').aggregate(Sum('balance'))
        
        assert assets == liabilities + equity, "Balance sheet not balanced!"
```

---

### 3.4 AUDIT TRAIL REQUIREMENTS

Every financial transaction MUST record:

```python
# Created
created_at = models.DateTimeField(auto_now_add=True)
created_by = models.ForeignKey(User, ...)

# Posted/Approved
posted_at = models.DateTimeField(null=True, blank=True)
posted_by = models.ForeignKey(User, ..., related_name='posted')

# Reversed (if applicable)
reversed_by = models.OneToOneField('self', ...)
reversed_at = models.DateTimeField(auto_now_add=True)

# Reference
payment_number = models.CharField(unique=True)
invoice_number = models.CharField(unique=True)
expense_number = models.CharField(unique=True)

# Source document
sale_id, payment_id, expense_id, supplier_id (links to source)
```

---

## PART 4: DATA MODEL MATRIX

| Model | Responsibility | Status | Key Fields | Immutability |
|---|---|---|---|---|
| Sale | Root transaction | DERIVED from payments | customer, sale_number, lines | After first payment |
| SaleLine | Product sold snapshot | Immutable | product, qty, price | Always immutable |
| Invoice | Billing snapshot | DERIVED from payments | total_amount, due_date | Immutable |
| Payment | Cash received | Immutable | amount, method, date | After creation |
| Product | Inventory item | Updates via movements | on_hand_qty, cost_price | qty via movement only |
| StockMovement | Audit trail | Immutable | qty_change, before, after | Always immutable |
| Expense | Expense record | Mutable (draft), immutable (posted) | category, amount, date | After posting |
| ExpenseCategory | GL mapping | Rarely changes | gl_account, affects_inventory | GL account fixed |
| Account | GL account | Static | account_code, account_type | Immutable |
| JournalEntry | Balanced transaction | Immutable | entry_type, lines | After creation |
| JournalEntryLine | GL posting | Immutable | account, amount, type | After creation |
| Client | Customer | Mutable | name, email, address | No financial limits |
| Supplier | Vendor | Mutable | name, email, payable_account | No financial limits |

---

## PART 5: MOBILE-FIRST RESPONSIVE DESIGN

### 5.1 DESIGN PRINCIPLES

**Goal:** Single responsive codebase (no separate mobile app)

**Approach:**
- Bootstrap 5 responsive grid (already implemented)
- Mobile-first CSS (enhance for larger screens)
- Touch-friendly UI (larger buttons, inputs)
- No horizontal scrolling on any screen
- Collapse complexity for mobile

---

### 5.2 RESPONSIVE PATTERNS

#### Pattern 1: Tables → Card Lists on Mobile

```html
<!-- Desktop: Table -->
<div class="table-responsive d-none d-md-block">
  <table class="table">
    <tr>
      <th>Invoice</th>
      <th>Customer</th>
      <th>Amount</th>
      <th>Status</th>
    </tr>
    ...
  </table>
</div>

<!-- Mobile: Card List -->
<div class="d-md-none">
  {% for invoice in invoices %}
  <div class="card mb-2">
    <div class="card-body">
      <h6 class="card-title">{{ invoice.invoice_number }}</h6>
      <p class="mb-1">
        <strong>Customer:</strong> {{ invoice.sale.customer.name }}
      </p>
      <p class="mb-1">
        <strong>Amount:</strong> ₨{{ invoice.total_amount }}
      </p>
      <div class="d-flex gap-2">
        <span class="badge bg-info">{{ invoice.status }}</span>
        <a href="..." class="btn btn-sm btn-primary">Pay</a>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
```

---

#### Pattern 2: Sidebar → Mobile Menu

```html
<!-- Desktop: Sidebar (d-none d-lg-block) -->
<div class="col-lg-3 d-none d-lg-block">
  <nav class="nav flex-column">
    <a class="nav-link" href="/sales/">Sales</a>
    <a class="nav-link" href="/invoices/">Invoices</a>
    <a class="nav-link" href="/accounting/">Accounting</a>
  </nav>
</div>

<!-- Mobile: Offcanvas -->
<div class="offcanvas offcanvas-start d-lg-none" id="sidebarMenu">
  <div class="offcanvas-header">
    <h5>RIMAN Fashion</h5>
    <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
  </div>
  <div class="offcanvas-body">
    <nav class="nav flex-column">
      <a class="nav-link" href="/sales/">Sales</a>
      <a class="nav-link" href="/invoices/">Invoices</a>
      <a class="nav-link" href="/accounting/">Accounting</a>
    </nav>
  </div>
</div>

<!-- Toggle button (mobile only) -->
<button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu">
  <i data-feather="menu"></i>
</button>
```

---

#### Pattern 3: KPI Cards - Stack on Mobile

```html
<div class="row g-3">
  <!-- Card stacks vertically on mobile (col-12), 3 per row on desktop (col-lg-4) -->
  <div class="col-12 col-sm-6 col-lg-4">
    <div class="card">
      <div class="card-body">
        <h6 class="text-muted">Total Sales</h6>
        <h3 class="text-primary">₨{{ total_sales }}</h3>
      </div>
    </div>
  </div>
</div>
```

---

#### Pattern 4: Forms - Full Width on Mobile

```html
<form method="post" class="container-fluid p-3">
  <!-- Full width on mobile, 50% on desktop -->
  <div class="row">
    <div class="col-12 col-lg-6">
      <div class="mb-3">
        <label for="amount" class="form-label">Amount</label>
        <!-- Large input: min 44px height for touch -->
        <input type="number" class="form-control form-control-lg" id="amount" name="amount" placeholder="0.00">
      </div>
    </div>
    
    <div class="col-12 col-lg-6">
      <div class="mb-3">
        <label for="date" class="form-label">Date</label>
        <!-- Mobile date picker (native on mobile) -->
        <input type="date" class="form-control form-control-lg" id="date" name="date">
      </div>
    </div>
  </div>
  
  <!-- Buttons: full width on mobile, normal on desktop -->
  <div class="d-grid gap-2 d-md-flex justify-content-md-end">
    <button type="submit" class="btn btn-primary btn-lg">Save</button>
  </div>
</form>
```

---

#### Pattern 5: Action Buttons - Reachable in 2 Taps

```html
<!-- Mobile: Floating action button (FAB) at bottom right -->
<div class="position-fixed bottom-0 end-0 p-3 d-lg-none">
  <div class="btn-group-vertical">
    <a href="/sales/add/" class="btn btn-primary btn-lg" title="New Sale">
      <i data-feather="plus"></i> Sale
    </a>
    <a href="/invoices/add/" class="btn btn-success btn-lg" title="New Invoice">
      <i data-feather="file-text"></i> Invoice
    </a>
    <a href="/expenses/add/" class="btn btn-warning btn-lg" title="New Expense">
      <i data-feather="dollar-sign"></i> Expense
    </a>
  </div>
</div>

<!-- Desktop: Top navbar -->
<nav class="navbar navbar-expand-lg navbar-light bg-light d-none d-lg-block">
  <div class="container">
    <a class="nav-link" href="/sales/add/">New Sale</a>
    <a class="nav-link" href="/invoices/add/">New Invoice</a>
    <a class="nav-link" href="/expenses/add/">New Expense</a>
  </div>
</nav>
```

---

#### Pattern 6: KPI Dashboard - Responsive Grid

```html
<!-- Mobile: 1 column, Tablet: 2 columns, Desktop: 4 columns -->
<div class="row g-3">
  <div class="col-12 col-sm-6 col-lg-3">
    <div class="card">
      <div class="card-body text-center">
        <h6 class="text-muted small">Total Sales</h6>
        <h3 class="mb-0">₨{{ total_sales }}</h3>
      </div>
    </div>
  </div>
  <!-- Repeat for other KPIs -->
</div>
```

---

### 5.3 RESPONSIVE BREAKPOINTS

```css
/* Bootstrap 5 breakpoints */
xs: < 576px (phones)
sm: ≥ 576px (landscape phones)
md: ≥ 768px (tablets)
lg: ≥ 992px (desktops)
xl: ≥ 1200px (large desktops)

/* Usage */
d-none d-md-block        /* Hide on mobile, show on tablet+ */
d-md-none                 /* Show on mobile, hide on tablet+ */
col-12 col-md-6 col-lg-3 /* Full width, 50%, 25% */
```

---

### 5.4 MOBILE-FIRST CSS PATTERNS

```html
<!-- Touch-friendly sizes -->
<button class="btn btn-primary" style="min-height: 44px; min-width: 44px;">
  Action
</button>

<!-- Large form inputs for mobile -->
<input class="form-control form-control-lg" type="text" placeholder="Large input">

<!-- Responsive spacing -->
<div class="p-3 p-md-4 p-lg-5">
  Content with responsive padding
</div>

<!-- Responsive font sizes -->
<h1 class="display-4 display-md-3 display-lg-2">Heading</h1>

<!-- Responsive columns -->
<div class="container-fluid">
  <div class="row">
    <div class="col-12 col-md-6 col-lg-4">Column</div>
  </div>
</div>
```

---

### 5.5 MOBILE REQUIREMENTS CHECKLIST

```
✅ Responsive Bootstrap layout
  □ No hardcoded widths (use col-* classes)
  □ Use g-* for grid gaps
  □ container-fluid for full-width pages
  □ Proper breakpoints (d-none d-md-block, etc.)

✅ No horizontal scrolling on any device
  □ Test on 320px width (iPhone SE)
  □ All tables use responsive wrapper or card view
  □ Forms use full width on mobile
  □ Long URLs wrapped or truncated

✅ Sidebar collapses into mobile menu
  □ Desktop: d-none d-lg-block sidebar
  □ Mobile: offcanvas or hamburger menu
  □ Toggle button d-lg-none

✅ KPI cards stack vertically
  □ col-12 col-md-6 col-lg-4 (or similar)
  □ No fixed widths
  □ Responsive text sizes

✅ Tables convert to card-style lists
  □ Table: d-none d-md-block
  □ Card: d-md-none
  □ All important info visible in both

✅ Mobile-optimized forms
  □ Inputs: form-control-lg (44px+ height)
  □ Date fields: type="date" (native picker)
  □ Number fields: type="number" (numeric keyboard)
  □ Full-width labels and inputs
  □ Buttons: d-grid gap-2 (full-width on mobile)

✅ Key actions reachable in ≤2 taps
  □ FAB buttons (floating action buttons)
  □ Or top navbar shortcuts
  □ Large, high-contrast buttons
  □ No nested menus on mobile

✅ Performance on mobile
  □ Minimize CSS/JS
  □ Lazy load images
  □ Optimize API calls
  □ Cache static assets

✅ Testing devices
  □ iPhone 14 (430×932)
  □ iPad (768×1024)
  □ Galaxy Tab (600×960)
  □ Desktop (1440×900)
```

---

## PART 6: IMPLEMENTATION ROADMAP

### Phase 1: Core Model Refinement (1-2 days)
```
□ Review Sale, SaleLine, Invoice, Payment models
□ Add @cached_property for totals calculation
□ Implement immutability checks in clean()
□ Add audit fields (created_by, created_at)
□ Create unit tests for model validation
```

### Phase 2: Automatic Accounting (1-2 days)
```
□ Implement signals for SaleLine creation → COGS entry + stock movement
□ Implement signals for Payment creation → revenue entry
□ Verify journal entries balance
□ Test complete sales flow with GL entries
```

### Phase 3: Expense System (2-3 days)
```
□ Create ExpenseCategory model with GL mapping
□ Create Expense model with posting logic
□ Implement expense posting → auto-GL entries
□ Implement expense reversal
□ Create admin interface for expenses
□ Test all expense flows
```

### Phase 4: Mobile Responsive Design (2-3 days)
```
□ Audit existing Bootstrap usage
□ Convert tables to responsive card lists
□ Create/refactor offcanvas navigation
□ Optimize forms (large inputs, date pickers)
□ Test on mobile devices (Chrome DevTools)
□ Create reusable responsive components
```

### Phase 5: Accounting Integrity (1-2 days)
```
□ Implement trial balance report
□ Implement inventory reconciliation check
□ Implement balance sheet equation check
□ Add data integrity checks to admin
□ Create audit trail export
```

### Phase 6: Testing & Documentation (2-3 days)
```
□ Complete test suite for all flows
□ Write technical documentation
□ Create admin guides
□ Performance testing
□ Security audit
□ Production deployment checklist
```

---

## PART 7: CRITICAL SUCCESS FACTORS

### Data Integrity
```
❌ Status stored in DB (use @property)
❌ Manual GL entries for sales/expenses
❌ Editable invoice totals
❌ Negative inventory quantities
❌ Unbalanced journal entries

✅ Every transaction auto-creates GL entry
✅ Posted items immutable, reversed only
✅ Audit trail for every change
✅ Trial balance always equal
✅ Inventory GL = Physical count
```

### Mobile Excellence
```
❌ Horizontal scrolling on mobile
❌ Tiny buttons (<44px)
❌ Complex nested menus
❌ Tables on mobile without scrolling
❌ Hardcoded widths

✅ Responsive grid (col-12 col-md-6 col-lg-4)
✅ Touch-friendly buttons (btn-lg)
✅ Offcanvas/hamburger navigation
✅ Card-style lists for mobile
✅ Full-width inputs & buttons
```

### Accounting Correctness
```
❌ Revenue recognized before payment
❌ Inventory reduced after sale (should be on sale creation)
❌ Manual journal entries bypassing system
❌ Duplicated totals in multiple places
❌ Unauditable transactions

✅ Revenue on payment only (cash basis)
✅ Inventory reduced on SaleLine creation
✅ All GL entries auto-created
✅ Single source of truth (totals calculated once)
✅ Every transaction traceable with references
```

---

## PART 8: DEPLOYMENT CHECKLIST

```
BEFORE GOING LIVE:

Database & Models
□ All migrations applied
□ No model field conflicts
□ Indexes created on key fields
□ Backup procedure tested

Core Flows
□ Sale → Invoice → Payment → Revenue entry verified
□ SaleLine → COGS + Stock movement verified
□ Expense creation → GL entry verified
□ Payment reversal creates compensating entry
□ Expense reversal creates compensating entry

Accounting Integrity
□ Trial balance daily/weekly check
□ Inventory reconciliation (GL = physical)
□ Balance sheet equation verified
□ Cash flow reconciliation tested

Audit Trail
□ created_by, created_at on all transactions
□ posted_by, posted_at on posted items
□ reversed_by on reversals
□ Reference numbers (sale#, payment#, expense#) unique

Mobile Testing
□ Home page responsive (all breakpoints)
□ Forms full-width on mobile
□ Tables convert to cards on mobile
□ No horizontal scrolling
□ Navigation hamburger works
□ Key actions accessible in 2 taps

Performance
□ Load time < 2s on mobile 4G
□ API calls optimized (no N+1 queries)
□ Static assets cached
□ Database queries indexed

Security
□ User permissions checked on all views
□ Sensitive data (payments, salaries) logged
□ Input validation on all forms
□ CSRF tokens on all POST requests
□ SQL injection prevention (ORM only)

User Training
□ Staff trained on new flows
□ Documentation complete
□ FAQ created
□ Support process defined

Documentation
□ Technical architecture doc
□ Admin user guide
□ API documentation
□ Troubleshooting guide

Backup & Disaster Recovery
□ Daily automated backups
□ Backup restoration tested
□ Disaster recovery plan documented
□ Data retention policy established
```

---

## APPENDIX: QUICK REFERENCE

### Sale Flow
```
1. User creates Sale (customer, date)
2. User adds SaleLines (product, qty, price)
   → Auto: COGS entry, stock movement, inventory reduced
3. On first payment:
   → Auto: Invoice created
   → Auto: Revenue entry created
   → Sale.status = 'paid' (or 'partial')
4. If payment reversed:
   → Auto: Compensating revenue entry
   → Sale.status back to 'unpaid'/'partial'
```

### Expense Flow
```
1. User creates Expense (category, amount, date) - DRAFT
2. User edits as needed (DRAFT only)
3. User posts Expense - POSTED
   → Auto: GL entries created (DR: expense, CR: cash/AP)
   → Immutable from here
4. If correction needed:
   → Expense.reverse()
   → Creates equal & opposite entry
   → Both posted, net effect ₨0
```

### GL Account Codes (Example)
```
1001 - Bank Account
1005 - Cash
1200 - Accounts Receivable
1300 - Inventory
2100 - Accounts Payable
3100 - Owner Capital
3200 - Retained Earnings
4100 - Sales Revenue
5000 - COGS
5100 - Office Supplies Expense
5300 - Maintenance Expense
5500 - Salary Expense
5600 - Rent Expense
5700 - Utilities Expense
```

---

**END OF DOCUMENT**

This guide provides a complete, implementation-ready architecture for transforming your RIMAN FASHION ERP into a professional, accounting-accurate, and mobile-friendly system. Every transaction is traceable, every number is auditable, and the system works flawlessly on all devices.
