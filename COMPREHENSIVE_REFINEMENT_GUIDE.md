# RIMAN FASHION ERP — COMPREHENSIVE REFINEMENT GUIDE
## Production-Grade Luxury Fashion Accounting & Operations System

**Last Updated:** January 27, 2026  
**Status:** Implementation-Ready  
**System:** Django 6.0.1 + PostgreSQL + Bootstrap 5  

---

## EXECUTIVE SUMMARY

This guide transforms RIMAN FASHION ERP from a basic sales system into a production-grade, double-entry accounting system handling luxury fashion operations: direct sales, rentals, custom manufacturing, and complex inventory workflows.

**Core Principle:** The system is a single source of truth for operations, inventory, and finance. Every transaction is immutable, traceable, and auditable.

---

## PART 1: SALES TYPES & BUSINESS LOGIC

### 1.1 Sales Type Definitions

#### **TYPE 1: DIRECT SALE (Immediate)**
```
Status Flow: Quote → Approved → Invoiced → Paid/Partial/Unpaid

Timeline:
- Product exists in inventory
- Customer orders
- Invoice issued immediately
- Inventory reduced immediately
- Revenue recognized on invoice date

Accounting:
  Debit: Accounts Receivable / Cash
  Credit: Sales Revenue
  
  Debit: Cost of Goods Sold
  Credit: Inventory Asset

Example: Wedding dress from ready stock → sold to customer → customer takes home
```

**Implementation:**
- No contract required
- Inventory check required before invoice
- Stock movement created automatically when invoice issued
- Revenue recognized immediately

---

#### **TYPE 2: RENTAL (Time-Limited)**
```
Status Flow: Contract (Draft→Approved→Ready) → Rental Active → Return → Closed

Timeline:
- Contract defines rental period, product, price, terms
- Contract approved and signed
- Product becomes "reserved" (inventory NOT reduced)
- Customer takes product on rental_start_date
- Product returned on rental_end_date
- Product returns to available inventory
- Final invoice issued at return

Accounting (at contract approval):
  Debit: Cash/Receivable (deposit)
  Credit: Unearned Revenue (Liability)

Accounting (at rental return):
  Debit: Unearned Revenue
  Credit: Rental Revenue
  
  Debit: Accounts Receivable (final invoice)
  Credit: Rental Revenue

Example: Evening gown rented for 3 days → customer deposits 30% → takes product → returns → final payment
```

**Implementation:**
- Contract MANDATORY
- Inventory reserved, NOT reduced
- Multiple invoice stream: Deposit invoice, Final invoice
- Revenue recognized on return date

---

#### **TYPE 3: CUSTOM-MADE FOR SALE**
```
Status Flow: Contract (Draft→Approved→InProduction→Ready→Invoiced) → Paid

Timeline:
- Product specifications defined in contract
- Deposits allowed (milestone payments)
- Production occurs
- Product enters inventory after production complete
- Final invoice issued at completion/delivery
- Revenue recognized only on final invoice

Accounting (Deposit):
  Debit: Cash
  Credit: Unearned Revenue (Liability)

Accounting (Production milestone):
  Debit: Accounts Receivable (interim invoice)
  Credit: Unearned Revenue

Accounting (Final):
  Debit: Accounts Receivable
  Credit: Sales Revenue
  
  Debit: Cost of Goods Sold
  Credit: Inventory

Example: Custom wedding dress → customer deposits 50% → production starts → interim invoice → final delivery → final payment
```

**Implementation:**
- Contract MANDATORY
- Inventory created automatically on production complete
- Multiple invoices allowed: Deposit invoice, Interim invoice(s), Final invoice
- Final invoice triggers inventory entry and revenue recognition

---

#### **TYPE 4: CUSTOM-MADE FOR RENT**
```
Status Flow: Contract (Draft→Approved→InProduction→Ready→RentalActive→Return→Closed)

Timeline:
- Product custom-produced for rental
- Deposits allowed
- Rental period defined
- Product created as rental asset after production
- Customer takes rental product
- Product returned
- Product retained as rental asset (retains value)
- Revenue recognized on return

Accounting (Deposit):
  Debit: Cash
  Credit: Unearned Revenue

Accounting (Production milestone):
  Debit: Rental Asset (Balance Sheet)
  Credit: Unearned Revenue

Accounting (Rental revenue):
  Debit: Unearned Revenue
  Credit: Rental Revenue

Example: Custom evening gown produced for rental → customer deposits → production → rental period → return → final payment
```

**Implementation:**
- Contract MANDATORY
- Inventory (rental asset) created on production complete
- Asset retained after rental (not reduced)
- Revenue recognized on return date

---

### 1.2 Sales Type Decision Matrix

| Scenario | Type | Contract Required | Inventory Impact | Invoice Timing | Revenue Recognition |
|----------|------|------------------|------------------|-----------------|---------------------|
| Buy ready dress | Direct Sale | NO | Reduce immediately | Immediate | Invoice date |
| Rent dress (3 days) | Rental | YES | Reserve only | At return | Return date |
| Custom dress (buy) | Custom Sale | YES | Create after production | At delivery | Final invoice date |
| Custom dress (rent) | Custom Rent | YES | Create as asset | At return | Return date |

---

## PART 2: CONTRACT SYSTEM (MANDATORY FOUNDATION)

### 2.1 Contract Model & Schema

```python
class Contract(models.Model):
    # Identification
    contract_number = CharField(unique=True)
    contract_type = CharField(choices=[
        ('rental', 'Rental'),
        ('custom_sale', 'Custom-Made for Sale'),
        ('custom_rent', 'Custom-Made for Rental'),
    ])
    
    # Parties
    client = ForeignKey(Client)
    sales_person = ForeignKey(User, null=True)
    
    # Product/Service Definition
    product_specification = TextField()  # Detailed description
    product = ForeignKey(Product, null=True, blank=True)  # Link if it exists
    
    # Timeline
    contract_date = DateField()
    rental_start_date = DateField(null=True, blank=True)
    rental_end_date = DateField(null=True, blank=True)
    production_start_date = DateField(null=True, blank=True)
    production_end_date = DateField(null=True, blank=True)
    delivery_date = DateField(null=True, blank=True)
    
    # Pricing
    total_price = DecimalField(max_digits=12, decimal_places=2)
    deposit_amount = DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit_due_date = DateField(null=True, blank=True)
    
    # Payment Schedule (Milestone-based)
    payment_schedule = JSONField(default=list)  # [{'date': '2026-02-01', 'amount': 5000, 'description': 'Milestone 1'}]
    
    # Status Lifecycle
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('in_production', 'In Production'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Immutability control
    invoicing_started_at = DateTimeField(null=True)  # Once set, contract becomes immutable
    
    # Terms
    notes = TextField()
    terms = TextField()  # Custom terms
    
    # Audit
    created_at = DateTimeField(auto_now_add=True)
    created_by = ForeignKey(User, related_name='contracts_created')
    approved_at = DateTimeField(null=True)
    approved_by = ForeignKey(User, related_name='contracts_approved', null=True)
    
    class Meta:
        ordering = ['-contract_date']
        indexes = [
            Index(fields=['contract_number']),
            Index(fields=['client', 'status']),
            Index(fields=['contract_type']),
        ]
    
    def __str__(self):
        return f"Contract {self.contract_number} - {self.client.name}"
    
    # BUSINESS RULES
    def can_edit(self):
        """Contract is immutable once invoicing starts"""
        return self.invoicing_started_at is None
    
    def can_invoice(self):
        """Can only invoice if contract is approved"""
        return self.status in ['approved', 'in_production', 'ready']
    
    def can_approve(self):
        """Can only approve if still in draft"""
        return self.status == 'draft'
    
    def get_remaining_balance(self):
        """Calculate amount still owed"""
        invoiced_total = sum(
            inv.total_amount for inv in self.invoices.filter(status='issued')
        )
        return self.total_price - invoiced_total
    
    def lock_for_invoicing(self):
        """Mark contract as invoicing started - becomes immutable"""
        self.invoicing_started_at = now()
        self.save()
```

---

### 2.2 Contract Lifecycle & Status Rules

```
DRAFT
  ├─ Can edit all fields
  ├─ Can add payment schedule
  └─ Action: Approve → APPROVED

APPROVED
  ├─ Immutable from here on
  ├─ Can issue deposit invoice
  ├─ For custom: Action: Start Production → IN_PRODUCTION
  └─ For rental: Waiting for rental_start_date

IN_PRODUCTION (Custom only)
  ├─ Production in progress
  ├─ Can issue milestone invoices
  ├─ Can update production_end_date
  └─ Action: Mark Ready → READY

READY
  ├─ Product complete/available
  ├─ For rental: Waiting for rental_start_date
  ├─ For custom sale: Awaiting final payment
  └─ Action: Complete → COMPLETED

COMPLETED
  ├─ All invoices paid or final issued
  ├─ No further changes
  └─ Archived

CANCELLED
  ├─ Contract voided
  ├─ All deposits reversed
  └─ No invoices allowed
```

---

### 2.3 Contract → Invoice Rules

**Rule 1: Deposit Invoice**
```
Allowed for: Rental, Custom Sale, Custom Rent
When: Contract approved
Amount: deposit_amount from contract
Status: PAID (if cash) or PENDING (if receivable)
```

**Rule 2: Interim/Milestone Invoices**
```
Allowed for: Custom Sale, Custom Rent
When: Payment schedule milestone reached
Amount: milestone amount from schedule
Status: PENDING until payment
```

**Rule 3: Final Invoice**
```
Allowed for: All types
When: All conditions met (rental returned, production complete, etc.)
Amount: Total price - (deposits + interim invoices)
Status: PENDING until payment
Accounting: Revenue recognition occurs here
```

---

## PART 3: INVOICING RULES (STRICT & AUDITABLE)

### 3.1 Invoice Model & Schema

```python
class Invoice(models.Model):
    # Identification
    invoice_number = CharField(unique=True)
    
    # Source (one required)
    sale = ForeignKey(Sale, null=True, blank=True)
    contract = ForeignKey(Contract, null=True, blank=True)
    
    # Type
    INVOICE_TYPE_CHOICES = [
        ('standard', 'Standard Invoice'),
        ('deposit', 'Deposit Invoice'),
        ('interim', 'Interim Invoice'),
        ('final', 'Final Invoice'),
    ]
    invoice_type = CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    
    # Dates
    invoice_date = DateField()
    due_date = DateField()
    
    # Line Items
    subtotal = DecimalField(max_digits=12, decimal_places=2)
    tax_amount = DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = DecimalField(max_digits=12, decimal_places=2)
    
    # Status (derived from payments, not stored)
    @property
    def status(self):
        """Derived from payments"""
        if self.amount_paid == 0:
            return 'unpaid'
        elif self.amount_paid < self.total_amount:
            return 'partial'
        else:
            return 'paid'
    
    # Control
    is_posted = BooleanField(default=False)  # Once true, immutable
    posted_at = DateTimeField(null=True)
    posted_by = ForeignKey(User, null=True)
    
    # Audit
    created_at = DateTimeField(auto_now_add=True)
    created_by = ForeignKey(User)
    
    class Meta:
        ordering = ['-invoice_date']
        unique_together = [['contract', 'invoice_type']]  # One of each type per contract
        indexes = [
            Index(fields=['invoice_number']),
            Index(fields=['contract', 'invoice_type']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    # BUSINESS RULES
    @property
    def amount_paid(self):
        """Sum of all non-reversed payments"""
        return sum(
            p.amount for p in self.payment_set.filter(reversed_at__isnull=True)
        )
    
    @property
    def amount_due(self):
        return self.total_amount - self.amount_paid
    
    def can_delete(self):
        """Invoice can only be deleted if not posted"""
        return not self.is_posted
    
    def post_to_gl(self):
        """Create journal entries"""
        if self.is_posted:
            raise Exception("Invoice already posted")
        
        # Debit: AR or Cash
        # Credit: Revenue (or Unearned Revenue reduction)
        
        # Additional: If sale (not contract), create COGS entry
        # Debit: COGS
        # Credit: Inventory
        
        self.is_posted = True
        self.posted_at = now()
        self.save()
```

---

### 3.2 Invoice Creation Rules

**Rule 1: Source Validation**
```
Every invoice MUST have one of:
  - A Sale (Direct Sales only)
  - A Contract (Rentals, Custom Sales, Custom Rents)

An invoice CANNOT have both.
An invoice CANNOT have neither.
```

**Rule 2: Contract-Based Invoicing**
```
IF invoice_type = 'deposit':
  ✓ Allowed only if contract.status in ['approved', 'in_production', 'ready']
  ✓ Amount = contract.deposit_amount
  ✓ Only ONE deposit invoice per contract

IF invoice_type = 'interim':
  ✓ Allowed only if contract.contract_type in ['custom_sale', 'custom_rent']
  ✓ Amount = next milestone payment from schedule
  ✓ Multiple allowed per contract

IF invoice_type = 'final':
  ✓ Allowed only if contract.status in ['ready', 'completed']
  ✓ For rental: only if rental_end_date has passed
  ✓ For custom: only if production_end_date has passed
  ✓ Amount = total_price - (deposits + interim invoices)
  ✓ Only ONE final invoice per contract
  ✓ TRIGGERS revenue recognition
```

**Rule 3: Sale-Based Invoicing**
```
IF source = Sale (Direct Sale only):
  ✓ One invoice per sale
  ✓ Amount = Sale total
  ✓ Inventory reduced at invoice creation
  ✓ Revenue recognized immediately
  ✓ No deposit/interim/final distinction
```

**Rule 4: Immutability**
```
ONCE invoice is posted (is_posted = True):
  ✗ Cannot edit amounts
  ✗ Cannot delete
  ✗ Cannot change dates
  ✓ Can receive payments
  ✓ Can issue credit memo (reversals only)
```

---

## PART 4: INVENTORY LOGIC (NON-NEGOTIABLE)

### 4.1 Inventory Model & Stock Movement

```python
class Product(models.Model):
    sku = CharField(unique=True)
    name = CharField()
    category = ForeignKey(Category)
    description = TextField()
    
    # Inventory Tracking
    quantity_in_stock = IntegerField(default=0)  # Available for sale/rental
    quantity_reserved = IntegerField(default=0)  # Reserved for rentals
    quantity_on_order = IntegerField(default=0)  # Awaiting production
    
    # Valuation
    cost_price = DecimalField(max_digits=12, decimal_places=2)
    sale_price = DecimalField(max_digits=12, decimal_places=2)
    rental_price_per_day = DecimalField(max_digits=12, decimal_places=2)
    
    # Type
    PRODUCT_TYPE_CHOICES = [
        ('ready_made', 'Ready-Made'),
        ('custom_made', 'Custom-Made'),
        ('rental_asset', 'Rental Asset'),
    ]
    product_type = CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    
    class Meta:
        indexes = [
            Index(fields=['sku']),
            Index(fields=['category']),
        ]
    
    @property
    def total_available(self):
        """Available for sale (not reserved)"""
        return self.quantity_in_stock - self.quantity_reserved
    
    @property
    def inventory_value(self):
        """Total asset value (at cost)"""
        return self.quantity_in_stock * self.cost_price
    
    def can_sell(self, quantity):
        """Check if product available for direct sale"""
        return self.total_available >= quantity
    
    def can_rent(self, quantity):
        """Check if product available for reservation"""
        return self.total_available >= quantity


class StockMovement(models.Model):
    """Immutable audit trail for all inventory changes"""
    
    MOVEMENT_TYPE_CHOICES = [
        ('initial', 'Initial Balance'),
        ('purchase', 'Purchase from Supplier'),
        ('sale', 'Sold via Direct Sale'),
        ('rental_reserve', 'Reserved for Rental'),
        ('rental_return', 'Returned from Rental'),
        ('custom_production', 'Produced (Custom)'),
        ('damage', 'Damaged/Loss'),
        ('adjustment', 'Manual Adjustment'),
        ('return', 'Customer Return'),
    ]
    
    # Reference
    movement_type = CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    
    # Product
    product = ForeignKey(Product)
    quantity_before = IntegerField()
    quantity_change = IntegerField()  # Positive or negative
    quantity_after = IntegerField()
    
    # Source Document
    sale = ForeignKey(Sale, null=True, blank=True)
    contract = ForeignKey(Contract, null=True, blank=True)
    purchase_order = ForeignKey(PurchaseOrder, null=True, blank=True)
    
    # Notes
    notes = TextField(blank=True)
    
    # Audit (IMMUTABLE)
    recorded_at = DateTimeField(auto_now_add=True)
    recorded_by = ForeignKey(User)
    
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            Index(fields=['product', '-recorded_at']),
            Index(fields=['movement_type']),
        ]
    
    def __str__(self):
        return f"{self.movement_type}: {self.product.sku} ({self.quantity_change:+d})"


class RentalReservation(models.Model):
    """Track which products are reserved for which rentals"""
    
    product = ForeignKey(Product)
    contract = ForeignKey(Contract)
    quantity_reserved = IntegerField()
    
    rental_start_date = DateField()
    rental_end_date = DateField()
    
    status = CharField(choices=[
        ('reserved', 'Reserved'),
        ('active', 'Active (Out with customer)'),
        ('returned', 'Returned'),
    ])
    
    returned_at = DateTimeField(null=True)
    returned_by = ForeignKey(User, null=True)
    
    class Meta:
        unique_together = [['product', 'contract']]
    
    def __str__(self):
        return f"Reserve: {self.product.sku} ({self.quantity_reserved}) for {self.contract.contract_number}"
```

---

### 4.2 Inventory Movement Rules

**Rule 1: Direct Sale Movement**
```
TRIGGER: Invoice issued for Direct Sale
ACTION: StockMovement created with type='sale'
  Before: quantity_in_stock = X
  Change: -quantity_sold
  After: quantity_in_stock = X - quantity_sold
CONSTRAINT: Must pass can_sell() check
RESULT: Inventory immediately reduced
```

**Rule 2: Rental Reservation**
```
TRIGGER: Contract approved for Rental
ACTION: RentalReservation created
  Product.quantity_reserved += quantity_reserved
  Product.quantity_in_stock unchanged
CONSTRAINT: Must pass can_rent() check
RESULT: Product not available for other sales, but still in stock

TRIGGER: Rental return
ACTION: RentalReservation.status = 'returned'
  Product.quantity_reserved -= quantity_reserved
RESULT: Product becomes available again
```

**Rule 3: Custom Production**
```
TRIGGER: Contract marked as 'in_production'
ACTION: Product created with quantity_in_stock = 0
  Product.quantity_on_order = 1

TRIGGER: Contract marked as 'ready'
ACTION: StockMovement created with type='custom_production'
  Product.quantity_on_order = 0
  Product.quantity_in_stock = 1
RESULT: Product now available in inventory

FOR CUSTOM RENTAL:
  Product.product_type = 'rental_asset'
  Product NOT reduced after rental (retains value)
```

**Rule 4: Rental Asset After Rental**
```
Custom Rental Asset Behavior:
  - Created during production with product_type='rental_asset'
  - After rental returns, quantity REMAINS in inventory
  - Can be rented again (reserved for next rental)
  - Never reduces due to rental
  - Only reduces if customer purchases it or it's damaged
```

**Rule 5: No Negative Inventory**
```
VALIDATION:
  For any movement, if quantity_after < 0:
    ✗ REJECT the transaction
    ✗ Return error: "Insufficient inventory"
```

**Rule 6: No Manual Edits**
```
✗ Cannot manually edit quantity_in_stock
✗ Cannot manually edit quantity_reserved
✓ Only through StockMovement (audit trail)

Exception: Initial inventory entry via Excel import
  - Import creates StockMovement records of type='initial'
  - Requires manager approval
  - Immutable after approval
```

---

## PART 5: EXPENSE MANAGEMENT

### 5.1 Expense Model

```python
class Expense(models.Model):
    # Identification
    expense_number = CharField(unique=True)
    
    # Core
    expense_date = DateField()
    amount = DecimalField(max_digits=12, decimal_places=2)
    
    # Category
    CATEGORY_CHOICES = [
        ('cogs', 'Cost of Goods Sold'),
        ('operating', 'Operating Expenses'),
        ('marketing', 'Marketing & Advertising'),
        ('maintenance', 'Maintenance & Cleaning'),
        ('admin', 'Administrative Expenses'),
        ('travel', 'Travel & Transportation'),
        ('utilities', 'Utilities'),
        ('other', 'Other'),
    ]
    category = CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Payment Method
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('cash_deposit', 'Cash Deposit'),
        ('atm_cash', 'ATM Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Credit Card'),
        ('cheque', 'Cheque'),
        ('payable', 'Accounts Payable'),
    ]
    payment_method = CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Links
    supplier = ForeignKey(Supplier, null=True, blank=True)
    product = ForeignKey(Product, null=True, blank=True)  # For COGS items
    contract = ForeignKey(Contract, null=True, blank=True)  # For contract-related
    
    # Detail
    description = TextField()
    reference = CharField(blank=True)  # Receipt#, Invoice#, etc.
    
    # Accounting
    is_posted = BooleanField(default=False)
    posted_at = DateTimeField(null=True)
    posted_by = ForeignKey(User, null=True)
    
    # If payable
    due_date = DateField(null=True, blank=True)
    paid_date = DateField(null=True, blank=True)
    
    # Audit
    created_at = DateTimeField(auto_now_add=True)
    created_by = ForeignKey(User)
    
    class Meta:
        ordering = ['-expense_date']
        indexes = [
            Index(fields=['category', '-expense_date']),
            Index(fields=['supplier']),
        ]
    
    def __str__(self):
        return f"Expense {self.expense_number} - {self.amount} ({self.category})"
    
    # BUSINESS RULES
    def can_edit(self):
        """Cannot edit posted expenses"""
        return not self.is_posted
    
    def post_to_gl(self):
        """Auto-generate GL entries on creation"""
        if self.is_posted:
            raise Exception("Already posted")
        
        # DEBIT: Expense account (based on category)
        # CREDIT: Cash / AR (based on payment method)
        
        if self.category == 'cogs' and self.product:
            # Increase product inventory value
            # Debit: Product Asset
            # Credit: Inventory Payable
        
        self.is_posted = True
        self.posted_at = now()
        self.save()
```

---

### 5.2 Expense Accounting Rules

**COGS Expenses (Inventory-Related)**
```
Trigger: Expense.category = 'cogs' AND product linked
Accounting:
  Debit: Inventory Asset (increases product cost)
  Credit: Cash / AP (depends on payment method)
Impact: Increases product value on balance sheet
```

**Operating Expenses**
```
Trigger: Expense category = 'operating', 'marketing', 'maintenance', 'admin'
Accounting:
  Debit: Expense account
  Credit: Cash / AP
Impact: Direct P&L impact (reduces profit)
```

**Payment Method Rules**
```
If payment_method = 'cash' or 'bank_transfer':
  Credit: Cash account
  Expense is IMMEDIATELY paid

If payment_method = 'payable':
  Credit: Accounts Payable
  Expense PENDING payment
  Track with due_date
  Pay later via payment transaction

If payment_method = 'card':
  Credit: Credit Card Payable (Liability)
  Settlement via bank reconciliation
```

**Immutability Rule**
```
ONCE posted:
  ✗ Cannot edit amount
  ✗ Cannot edit category
  ✗ Cannot delete
  ✓ Can record payment (if AP)
  ✓ Can reverse via reversal entry (correction)
```

---

## PART 6: ACCOUNTING INTEGRITY (DOUBLE-ENTRY FOUNDATION)

### 6.1 Chart of Accounts

```python
# ASSETS (1000-1999)
1000 - Cash
1100 - Accounts Receivable
1200 - Inventory - Ready Made
1201 - Inventory - Custom Made
1202 - Rental Assets
1300 - Prepaid Expenses

# LIABILITIES (2000-2999)
2000 - Accounts Payable
2100 - Unearned Revenue (Deposits)
2200 - Credit Card Payable
2300 - Short-term Loans

# EQUITY (3000-3999)
3000 - Owner's Capital
3100 - Retained Earnings

# REVENUE (4000-4999)
4000 - Sales Revenue (Direct)
4100 - Rental Revenue
4200 - Custom Sale Revenue
4300 - Custom Rental Revenue

# COST OF GOODS SOLD (5000-5999)
5000 - Cost of Goods Sold

# OPERATING EXPENSES (6000-6999)
6000 - Marketing & Advertising
6100 - Maintenance & Cleaning
6200 - Administrative Expenses
6300 - Travel & Transportation
6400 - Utilities
6500 - Other Operating Expenses
```

---

### 6.2 Journal Entry Rules

**Rule 1: Every transaction creates double-entry**
```
No single-line entries.
Debits = Credits.
Always balanced.
```

**Rule 2: Source Documentation**
```
Every JournalEntry MUST reference:
  - sale (for Direct Sale GL entries)
  - contract (for Contract-based GL entries)
  - invoice (for revenue recognition)
  - expense (for expense entries)
  - payment (for cash entries)

No orphan entries.
Immutable traceability.
```

**Rule 3: Posting Logic**

```
DIRECT SALE → Invoice Created:
  Debit: 1100 AR / 1000 Cash
  Credit: 4000 Sales Revenue

  Debit: 5000 COGS
  Credit: 1200 Inventory

RENTAL DEPOSIT → Deposit Invoice:
  Debit: 1000 Cash / 1100 AR
  Credit: 2100 Unearned Revenue (Liability)

RENTAL RETURN → Final Invoice:
  Debit: 2100 Unearned Revenue
  Credit: 4100 Rental Revenue

CUSTOM SALE INTERIM → Interim Invoice:
  Debit: 1100 AR
  Credit: 2100 Unearned Revenue (reduces liability)

CUSTOM PRODUCTION → Inventory Created:
  Debit: 1201 Custom Inventory
  Credit: 2100 Unearned Revenue

EXPENSE → Cash/AP:
  Debit: 6xxx Operating Expense
  Credit: 1000 Cash OR 2000 AP

PAYMENT → Receivable:
  Debit: 1000 Cash / 2000 AP
  Credit: 1100 AR / 2100 Unearned Revenue
```

---

### 6.3 Reconciliation Rules

**Rule 1: Balance Sheet**
```
Assets = Liabilities + Equity

Must be true at all times.
No exceptions.
```

**Rule 2: Revenue Recognition**
```
Revenue is recorded ONLY when:
  ✓ Invoice is posted
  ✓ Customer obligation is satisfied
  ✓ Payment is reasonably assured (for accrual)

For Direct Sales: On invoice date
For Rentals: On return date
For Custom Sales: On final invoice date
For Custom Rentals: On return date
```

**Rule 3: GL Reconciliation to Sub-ledgers**
```
AR Balance = Sum(Unpaid Invoices)
Inventory Balance = Sum(Product quantities × cost)
Unearned Revenue = Sum(Deposits not yet recognized)
Accounts Payable = Sum(Unpaid Expenses & Bills)
```

---

## PART 7: REPORTING ARCHITECTURE

### 7.1 Report Templates (Time-Based)

All reports support:
- Weekly (Monday-Sunday)
- Monthly (1st-last day)
- Yearly (Jan 1 - Dec 31)
- Custom date range

---

### 7.2 Required Reports

#### **Report 1: Sales Summary**
```
Metrics:
  - Total Sales Revenue
  - Total Rental Revenue
  - Total Custom Revenue
  - Average Transaction Value
  - Number of Transactions

Breakdown by Type:
  Direct Sales count & revenue
  Rental count & revenue
  Custom count & revenue

Breakdown by Client:
  Top 10 clients by revenue

CSV Export | PDF | Print
```

#### **Report 2: Profit & Loss**
```
Format:
  Revenue (4000-4300)
    - Direct Sales Revenue
    - Rental Revenue
    - Custom Revenue
  Less: COGS (5000)
  Gross Margin
  
  Operating Expenses (6000-6500)
    - By category
  
  Operating Profit
  
  Other Income/Expense
  
  Net Income

Period: Month/Quarter/Year
Comparison: Prior period
Export: PDF, Excel
```

#### **Report 3: Cash Flow Summary**
```
Operating Activities:
  Revenue received
  Expenses paid
  Net Operating Cash Flow

Investing Activities:
  Asset purchases
  Asset sales

Financing Activities:
  Owner deposits
  Loan proceeds

Ending Cash Balance

Format: Month/Quarter
```

#### **Report 4: Inventory Valuation**
```
By Product:
  SKU | Qty | Cost Price | Total Value
  
Subtotals by Category

Total Inventory Value

Status:
  Available for sale
  Reserved for rental
  On order

CSV Export | Reorder Report
```

#### **Report 5: Contract Pipeline**
```
Active Contracts:
  Contract # | Type | Client | Amount | % Complete | Status

Projected Revenue:
  By month (from contract delivery dates)
  Confirmed vs. at-risk

Deposit Received:
  Amount | %

Outstanding:
  Amount | %

CSV Export
```

#### **Report 6: Client Balances**
```
By Client:
  Name | Total Sales | Amount Paid | Outstanding | Status

Aging:
  Current
  30 days
  60 days
  90+ days

Outstanding AR by client

Collections status
```

#### **Report 7: Expense Summary**
```
By Category:
  Operating
  COGS
  Marketing
  Maintenance
  Admin
  Other

By Supplier (if applicable)

Paid vs. Unpaid (AP)

PDF | Excel
```

#### **Report 8: GL Trial Balance**
```
Account # | Account Name | Debit | Credit

Total Debits | Total Credits

Verify: Debits = Credits

Previous period comparison
```

---

### 7.3 Report Implementation

```python
class ReportService:
    """Generate all reports from GL data"""
    
    def __init__(self, date_from, date_to):
        self.date_from = date_from
        self.date_to = date_to
    
    def get_sales_summary(self):
        """Aggregate sales by type"""
        invoices = Invoice.objects.filter(
            invoice_date__range=[self.date_from, self.date_to],
            is_posted=True
        )
        # ... calculations
        return {
            'total_revenue': Decimal,
            'by_type': dict,
            'by_client': dict,
        }
    
    def get_profit_loss(self):
        """Calculate P&L from GL"""
        revenue = sum_gl_range(4000, 4999)
        cogs = sum_gl_range(5000, 5999)
        operating = sum_gl_range(6000, 6999)
        
        gross_margin = revenue - cogs
        net_income = gross_margin - operating
        
        return {...}
    
    def export_to_pdf(self, report_type):
        """Generate PDF"""
        # Use reportlab
    
    def export_to_excel(self, report_type):
        """Generate Excel"""
        # Use openpyxl

class ReportView(LoginRequiredMixin, TemplateView):
    """Display reports with filtering"""
    
    def get_context_data(self, **kwargs):
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        service = ReportService(date_from, date_to)
        return {
            'report_data': service.get_sales_summary(),
            'date_from': date_from,
            'date_to': date_to,
        }
```

---

## PART 8: PRINT & PREVIEW ARCHITECTURE

### 8.1 Print Templates

**All printables use:**
- RIMAN FASHION branding (header + logo)
- Company details (address, phone, tax ID)
- Period/date information
- Data table
- Footer with "Report Date" and page info

---

### 8.2 Printable Documents

```
1. Sales Invoice
   - Invoice #, date, due date
   - Bill To (client)
   - Line items (description, qty, price, total)
   - Subtotal, Tax, Total
   - Payment terms
   - QR code (optional)

2. Rental Contract (PDF)
   - Contract #, dates
   - Product specs
   - Price breakdown
   - Payment schedule
   - Terms & conditions
   - Signature lines

3. Expense Report
   - Period
   - By category table
   - Grand total
   - Approver line

4. Client Statement
   - Client info
   - Date range
   - Transactions table (date, description, amount, balance)
   - Outstanding balance
   - Due date

5. Inventory Report
   - Product list
   - Qty, Cost, Value
   - Status (Available/Reserved/On-Order)
   - Total value
```

---

### 8.3 Print Implementation

```python
class PrintableReportMixin:
    """Base for all printable documents"""
    
    def get_pdf_buffer(self):
        """Return PDF buffer for download"""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Header
        elements.append(Paragraph("RIMAN FASHION ERP", styles['Title']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Content
        # ... build document
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def get(self, request, *args, **kwargs):
        format = request.GET.get('format', 'html')
        
        if format == 'pdf':
            pdf = self.get_pdf_buffer()
            return FileResponse(pdf, filename='report.pdf')
        
        elif format == 'print':
            return render(request, 'print_template.html', self.get_context())
        
        else:  # html
            return render(request, 'report_template.html', self.get_context())
```

---

## PART 9: MOBILE-FRIENDLY RESPONSIVE DESIGN

### 9.1 Bootstrap 5 Responsive Framework

```html
<!-- Base Template -->
<div class="container-fluid">
    <!-- Mobile Navigation: Sidebar Collapse -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <button class="navbar-toggler" data-bs-toggle="offcanvas">
            <span class="navbar-toggler-icon"></span>
        </button>
    </nav>
    
    <!-- Sidebar: Collapses on Mobile -->
    <div class="offcanvas offcanvas-start" id="sidebar">
        <nav>
            <!-- Navigation items -->
        </nav>
    </div>
    
    <!-- Main Content -->
    <div class="content">
        <!-- Page content -->
    </div>
</div>
```

### 9.2 Responsive Components

**KPI Cards (Mobile Stack)**
```html
<div class="row g-3">
    <div class="col-12 col-md-6 col-lg-3">
        <div class="card">
            <div class="card-body">
                <h6>Revenue</h6>
                <h3>$10,000</h3>
            </div>
        </div>
    </div>
    <!-- Stack vertically on mobile -->
</div>
```

**Tables Convert to Cards**
```html
<!-- Desktop: Table -->
<div class="d-none d-md-block">
    <table class="table">...</table>
</div>

<!-- Mobile: Cards -->
<div class="d-md-none">
    {% for item in items %}
    <div class="card mb-3">
        <div class="card-body">
            {{ item.name }}: {{ item.value }}
        </div>
    </div>
    {% endfor %}
</div>
```

**Forms (Touch-Optimized)**
```html
<form>
    <!-- Larger input areas -->
    <input type="text" class="form-control form-control-lg">
    
    <!-- Buttons within 2-tap reach -->
    <button class="btn btn-lg btn-primary mt-3">Submit</button>
</form>
```

---

## PART 10: DASHBOARD ARCHITECTURE

### 10.1 Dashboard Data Model

```python
class DashboardData:
    """Unified KPI source"""
    
    def __init__(self, date_from, date_to):
        self.date_from = date_from
        self.date_to = date_to
    
    @property
    def total_revenue(self):
        """From GL 4000-4300"""
        return sum_gl_account_range(4000, 4300, self.date_from, self.date_to)
    
    @property
    def total_expenses(self):
        """From GL 6000-6999"""
        return sum_gl_account_range(6000, 6999, self.date_from, self.date_to)
    
    @property
    def net_profit(self):
        """Revenue - Expenses - COGS"""
        cogs = sum_gl_account_range(5000, 5999, self.date_from, self.date_to)
        return self.total_revenue - self.total_expenses - cogs
    
    @property
    def outstanding_receivables(self):
        """AR - Payments"""
        unpaid = Invoice.objects.filter(
            invoice_date__range=[self.date_from, self.date_to]
        ).aggregate(unpaid=Sum('amount_due'))
        return unpaid['unpaid'] or 0
    
    @property
    def available_inventory_value(self):
        """Available qty × cost"""
        return sum(
            p.total_available * p.cost_price 
            for p in Product.objects.all()
        )
    
    @property
    def reserved_inventory_value(self):
        """Reserved qty × cost"""
        return sum(
            p.quantity_reserved * p.cost_price 
            for p in Product.objects.all()
        )
```

### 10.2 Dashboard UI

```html
<!-- Dashboard View -->
<div class="row">
    <!-- KPI Row -->
    <div class="col-12 col-md-6 col-lg-3">
        <a href="{% url 'sales_report' %}">
            <div class="card kpi-card">
                <h6>Total Revenue</h6>
                <h2>{{ dashboard.total_revenue|currency }}</h2>
            </div>
        </a>
    </div>
    
    <div class="col-12 col-md-6 col-lg-3">
        <a href="{% url 'expense_report' %}">
            <div class="card kpi-card">
                <h6>Total Expenses</h6>
                <h2>{{ dashboard.total_expenses|currency }}</h2>
            </div>
        </a>
    </div>
    
    <div class="col-12 col-md-6 col-lg-3">
        <div class="card kpi-card">
            <h6>Net Profit</h6>
            <h2 class="text-success">{{ dashboard.net_profit|currency }}</h2>
        </div>
    </div>
    
    <div class="col-12 col-md-6 col-lg-3">
        <a href="{% url 'inventory_report' %}">
            <div class="card kpi-card">
                <h6>Outstanding AR</h6>
                <h2>{{ dashboard.outstanding_receivables|currency }}</h2>
            </div>
        </a>
    </div>
</div>

<!-- Inventory Row -->
<div class="row mt-4">
    <div class="col-12 col-md-6">
        <div class="card">
            <h5>Inventory Status</h5>
            <table class="table">
                <tr>
                    <td>Available</td>
                    <td class="text-end">{{ dashboard.available_inventory_value|currency }}</td>
                </tr>
                <tr>
                    <td>Reserved</td>
                    <td class="text-end">{{ dashboard.reserved_inventory_value|currency }}</td>
                </tr>
            </table>
        </div>
    </div>
    
    <div class="col-12 col-md-6">
        <div class="card">
            <h5>Recent Invoices</h5>
            <!-- List of recent invoices -->
        </div>
    </div>
</div>
```

---

## PART 11: EXCEL IMPORT/EXPORT WORKFLOW

### 11.1 Import Process

**Import Validation Flow:**
```
1. User uploads Excel file
2. Parse file structure
3. Validate column headers
4. Validate each row:
   - Required fields present
   - Data types correct
   - No duplicate SKUs/client codes
   - Quantity > 0
   - Prices >= 0
5. Preview errors (if any)
6. User confirms
7. Create records in transaction
8. Rollback if any error
```

### 11.2 Import Templates

**Template 1: Products Import**
```
SKU | Name | Category | Cost Price | Sale Price | Rental Price/Day | Qty | Type
ABC001 | Wedding Dress | Wedding | 500.00 | 1500.00 | 50.00 | 5 | ready_made
```

**Template 2: Clients Import**
```
Client Code | Name | Email | Phone | City | Address | Type
CL001 | Jane Smith | jane@email.com | 555-1234 | Dubai | 123 Main St | Individual
```

**Template 3: Expenses Import**
```
Date | Amount | Category | Payment Method | Supplier | Description | Reference
2026-01-15 | 250.00 | maintenance | cash | ABC Cleaning | Venue cleaning | RCP-001
```

**Template 4: Opening Inventory**
```
SKU | Product Name | Qty | Cost Price
ABC001 | Wedding Dress | 10 | 500.00
```

---

### 11.3 Export Process

```python
class ExportService:
    @staticmethod
    def export_sales_report(date_from, date_to):
        """Export sales to Excel"""
        workbook = Workbook()
        sheet = workbook.active
        
        # Headers
        sheet.append(['Date', 'Invoice #', 'Client', 'Amount', 'Type', 'Status'])
        
        # Data
        for invoice in Invoice.objects.filter(
            invoice_date__range=[date_from, date_to]
        ):
            sheet.append([
                invoice.invoice_date,
                invoice.invoice_number,
                invoice.contract.client.name if invoice.contract else invoice.sale.customer.name,
                invoice.total_amount,
                invoice.invoice_type,
                invoice.status,
            ])
        
        # Format and return
        return workbook
```

---

## PART 12: SYSTEM SAFEGUARDS & VALIDATIONS

### 12.1 Critical Validation Rules

```python
class BusinessLogicValidator:
    """Enforce all business rules"""
    
    @staticmethod
    def validate_invoice_creation(invoice_data):
        """Cannot create invalid invoices"""
        
        # 1. Source validation
        if not invoice_data.get('sale') and not invoice_data.get('contract'):
            raise ValidationError("Invoice must have Sale OR Contract")
        
        if invoice_data.get('sale') and invoice_data.get('contract'):
            raise ValidationError("Invoice cannot have both Sale and Contract")
        
        # 2. Contract-based validation
        if invoice_data.get('contract'):
            contract = invoice_data['contract']
            
            if not contract.can_invoice():
                raise ValidationError(f"Contract status {contract.status} cannot be invoiced")
            
            if invoice_data['invoice_type'] == 'deposit':
                if Invoice.objects.filter(
                    contract=contract, 
                    invoice_type='deposit'
                ).exists():
                    raise ValidationError("Deposit invoice already exists for this contract")
            
            if invoice_data['invoice_type'] == 'final':
                if contract.contract_type == 'rental':
                    if contract.rental_end_date > today():
                        raise ValidationError("Cannot issue final invoice before rental ends")
        
        # 3. Amount validation
        if invoice_data['total_amount'] <= 0:
            raise ValidationError("Invoice amount must be > 0")
        
        return True
    
    @staticmethod
    def validate_stock_movement(movement_data):
        """Ensure inventory consistency"""
        
        product = movement_data['product']
        quantity = movement_data['quantity_change']
        
        # Check: No negative inventory
        new_qty = product.quantity_in_stock + quantity
        if new_qty < 0:
            raise ValidationError(f"Insufficient inventory for {product.sku}")
        
        # Check: No negative reservation
        if movement_data['type'] == 'rental_return':
            new_reserved = product.quantity_reserved - quantity
            if new_reserved < 0:
                raise ValidationError("Reservation mismatch")
        
        return True
    
    @staticmethod
    def validate_expense_posting(expense):
        """Ensure GL entries valid"""
        
        # Cannot edit posted
        if expense.is_posted:
            raise ValidationError("Expense already posted")
        
        # Amount valid
        if expense.amount <= 0:
            raise ValidationError("Expense must be > 0")
        
        return True
    
    @staticmethod
    def validate_contract_edit(contract, changes):
        """Contract immutability"""
        
        if contract.invoicing_started_at:
            raise ValidationError("Contract is immutable (invoicing started)")
        
        if contract.status not in ['draft']:
            if 'status' in changes:
                # Only allow specific transitions
                allowed_next = {
                    'approved': ['in_production', 'ready', 'cancelled'],
                    'in_production': ['ready', 'cancelled'],
                    'ready': ['completed', 'cancelled'],
                }
                
                if changes['status'] not in allowed_next.get(contract.status, []):
                    raise ValidationError(f"Invalid status transition")
        
        return True
```

---

### 12.2 Audit Trail

```python
class AuditLog(models.Model):
    """Immutable record of all changes"""
    
    timestamp = DateTimeField(auto_now_add=True)
    user = ForeignKey(User)
    action = CharField()  # create, update, delete, post
    model_name = CharField()  # Invoice, Contract, etc.
    object_id = CharField()
    changes = JSONField()  # Old values vs new values
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            Index(fields=['timestamp']),
            Index(fields=['user']),
        ]
    
    @staticmethod
    def log_change(user, action, model, obj_id, old_values, new_values):
        """Record every change"""
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model.__name__,
            object_id=obj_id,
            changes={'old': old_values, 'new': new_values}
        )
```

---

## PART 13: IMPLEMENTATION ROADMAP

### Phase 1: Contract System (Weeks 1-2)
- [ ] Create Contract model
- [ ] Contract status lifecycle
- [ ] Contract → Invoice logic
- [ ] Migration & testing

### Phase 2: Invoicing Rules (Weeks 3-4)
- [ ] Enhance Invoice model
- [ ] Deposit/Interim/Final logic
- [ ] Invoice-to-GL posting
- [ ] Immutability enforcement

### Phase 3: Inventory Overhaul (Weeks 5-6)
- [ ] StockMovement creation
- [ ] Rental reservation logic
- [ ] Inventory value calculations
- [ ] No manual edits enforcement

### Phase 4: Expense Management (Week 7)
- [ ] Expense model
- [ ] Automatic GL posting
- [ ] Reversal entries
- [ ] AP tracking

### Phase 5: GL & Accounting (Week 8)
- [ ] GL posting rules
- [ ] Trial balance
- [ ] Reconciliation reports
- [ ] Integrity checks

### Phase 6: Reporting (Weeks 9-10)
- [ ] All report types
- [ ] PDF/Excel export
- [ ] Date filtering
- [ ] Performance optimization

### Phase 7: Mobile & UX (Week 11)
- [ ] Bootstrap responsive
- [ ] Mobile tables → cards
- [ ] Touch-optimized forms
- [ ] Testing on devices

### Phase 8: Testing & Polish (Week 12)
- [ ] Integration testing
- [ ] UAT with business
- [ ] Documentation
- [ ] Production deployment

---

## PART 14: DATA INTEGRITY CHECKLIST

**Before Production:**

- [ ] GL balances (Debits = Credits)
- [ ] AR reconciles (AR balance = unpaid invoices)
- [ ] Inventory reconciles (GL inventory = sum of products)
- [ ] AP reconciles (AP balance = unpaid expenses)
- [ ] Cash balance verified
- [ ] Contract pipeline matches revenue projections
- [ ] All posted documents auditable to source
- [ ] No orphan GL entries
- [ ] No duplicate invoices
- [ ] No negative inventory occurrences

---

## CONCLUSION

This system transforms RIMAN FASHION ERP into an enterprise-grade accounting platform. Every transaction is:

✅ **Immutable** - Cannot be edited after posting
✅ **Traceable** - Auditable to source documents
✅ **Balanced** - Double-entry at all times
✅ **Compliant** - Business rules enforced programmatically
✅ **Printable** - Professional reports & PDFs
✅ **Mobile** - Fully responsive
✅ **Real-time** - Dashboard reflects actual data
✅ **Production-ready** - Suitable for daily operations and audits

---

**Next Steps:**
1. Review this guide with business stakeholders
2. Validate against actual business workflows
3. Create database migrations
4. Implement Phase 1 (Contracts)
5. Build test cases
6. Deploy incrementally with UAT

**Success Criteria:**
- System prevents invalid transactions
- All GL reports reconcile perfectly
- Audit trail is complete and immutable
- Mobile works without UI clutter
- Print PDFs look professional
- Stakeholders confirm system matches operations
