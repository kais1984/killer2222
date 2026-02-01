"""
Accounting Models: Financial transactions, P&L, assets, liabilities
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, timedelta

class ChartOfAccounts(models.Model):
    """Chart of Accounts for accounting structure"""
    
    ACCOUNT_TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
        ('cost_of_goods', 'Cost of Goods Sold'),
    ]
    
    ACCOUNT_CATEGORY_CHOICES = [
        ('current_asset', 'Current Asset'),
        ('fixed_asset', 'Fixed Asset'),
        ('current_liability', 'Current Liability'),
        ('long_term_liability', 'Long-term Liability'),
        ('sales_revenue', 'Sales Revenue'),
        ('rental_revenue', 'Rental Revenue'),
        ('operating_expense', 'Operating Expense'),
        ('cost_of_materials', 'Cost of Materials'),
        ('cost_of_labor', 'Cost of Labor'),
    ]
    
    account_code = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    account_category = models.CharField(max_length=30, choices=ACCOUNT_CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Audit Trail
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chart_of_accounts_created'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chart_of_accounts_updated'
    )
    
    class Meta:
        ordering = ['account_code']
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"


class JournalEntry(models.Model):
    """Double-entry journal entry"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('void', 'Void'),
    ]
    
    entry_date = models.DateField()
    reference_number = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    total_debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_by = models.CharField(max_length=255, blank=True)
    approved_by = models.CharField(max_length=255, blank=True, null=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-entry_date']
        indexes = [
            models.Index(fields=['entry_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Journal Entry {self.reference_number}"


class JournalEntryLine(models.Model):
    """Individual line item in a journal entry"""
    
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE)
    
    debit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                       validators=[MinValueValidator(0)])
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                        validators=[MinValueValidator(0)])
    
    description = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.account.account_code}"


class Income(models.Model):
    """Income/Revenue tracking"""
    
    INCOME_TYPE_CHOICES = [
        ('sales', 'Sales Revenue'),
        ('rental', 'Rental Revenue'),
        ('custom_order', 'Custom Order'),
        ('service', 'Service Revenue'),
        ('other', 'Other Income'),
    ]
    
    income_date = models.DateField()
    income_type = models.CharField(max_length=20, choices=INCOME_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-income_date']
    
    def __str__(self):
        return f"{self.get_income_type_display()} - {self.amount}"


class Expense(models.Model):
    """Expense tracking with GL posting support (Phase 3)"""
    
    EXPENSE_TYPE_CHOICES = [
        ('supplies', 'Supplies & Materials'),
        ('labor', 'Labor Costs'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('marketing', 'Marketing & Advertising'),
        ('transportation', 'Transportation'),
        ('maintenance', 'Maintenance & Repairs'),
        ('salaries', 'Salaries & Wages'),
        ('other', 'Other Expenses'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('posted', 'Posted to GL'),
        ('rejected', 'Rejected'),
    ]
    
    # Expense identification
    expense_number = models.CharField(max_length=50, unique=True, editable=False, default='EXP-AUTO')  # EXP-YYYYMMDD-XXXXXX
    expense_date = models.DateField()
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    
    # Financial details
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.SET_NULL, null=True, blank=True,
                               limit_choices_to={'account_type': 'expense'})
    
    # Supplier/source
    supplier = models.CharField(max_length=255, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    receipt_file = models.FileField(upload_to='expenses/', blank=True, null=True)
    
    # GL posting control
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(blank=True, null=True)
    posted_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='expenses_posted')
    gl_posted = models.BooleanField(default=False)
    
    # Approval workflow
    submitted_at = models.DateTimeField(blank=True, null=True)
    submitted_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='expenses_submitted')
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='expenses_approved')
    
    # Audit trail
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='expenses_created')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
        indexes = [
            models.Index(fields=['expense_date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_posted']),
        ]
    
    def __str__(self):
        return f"{self.expense_number} - {self.get_expense_type_display()} - {self.amount}"
    
    def save(self, *args, **kwargs):
        """Auto-generate expense number if not set"""
        if self.expense_number == 'EXP-AUTO' or not self.expense_number:
            import random
            today = timezone.now().strftime('%Y%m%d')
            random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            self.expense_number = f"EXP-{today}-{random_suffix}"
        super().save(*args, **kwargs)
    
    def can_edit(self):
        """Check if expense can be edited"""
        return self.status in ['draft', 'rejected']
    
    def can_delete(self):
        """Check if expense can be deleted"""
        return self.status in ['draft', 'rejected']
    
    def can_approve(self):
        """Check if expense can be approved"""
        return self.status == 'submitted'
    
    def can_reject(self):
        """Check if expense can be rejected"""
        return self.status in ['draft', 'submitted']
    
    def post_to_gl(self, user=None):
        """
        Post expense to GL (create journal entry).
        Debit: Expense Account
        Credit: Cash/Accounts Payable
        """
        if self.is_posted or self.status != 'approved':
            raise ValueError("Expense must be approved and not yet posted")
        
        if not self.account:
            raise ValueError("Expense must have an account assigned")
        
        from financeaccounting.models import JournalEntry, JournalEntryLine
        from financeaccounting.services import ExpenseAccountingService
        
        try:
            # Use accounting service to post
            ExpenseAccountingService.post_expense(self, user)
            self.is_posted = True
            self.posted_at = timezone.now()
            self.posted_by = user
            self.gl_posted = True
            self.status = 'posted'
            self.save()
        except Exception as e:
            raise ValueError(f"Failed to post expense to GL: {str(e)}")


class Asset(models.Model):
    """Asset tracking"""
    
    ASSET_TYPE_CHOICES = [
        ('equipment', 'Equipment'),
        ('furniture', 'Furniture'),
        ('vehicle', 'Vehicle'),
        ('property', 'Property'),
        ('other', 'Other'),
    ]
    
    asset_name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    purchase_date = models.DateField()
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2)
    accumulated_depreciation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    useful_life_years = models.IntegerField(default=5)
    annual_depreciation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    is_active = models.BooleanField(default=True)
    disposal_date = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-purchase_date']
    
    def __str__(self):
        return self.asset_name
    
    def calculate_book_value(self):
        return self.acquisition_cost - self.accumulated_depreciation


class Liability(models.Model):
    """Liability tracking"""
    
    LIABILITY_TYPE_CHOICES = [
        ('accounts_payable', 'Accounts Payable'),
        ('salary_payable', 'Salary Payable'),
        ('loan', 'Loan'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other'),
    ]
    
    liability_name = models.CharField(max_length=255)
    liability_type = models.CharField(max_length=30, choices=LIABILITY_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    due_date = models.DateField(blank=True, null=True)
    
    is_paid_off = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return self.liability_name


class FinancialPeriod(models.Model):
    """Financial closing period"""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('locked', 'Locked'),
        ('closed', 'Closed'),
    ]
    
    period_start = models.DateField()
    period_end = models.DateField()
    period_name = models.CharField(max_length=50)  # e.g., "January 2024"
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    opening_inventory_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_inventory_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_profit_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    locked_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period_start']
        unique_together = ['period_start', 'period_end']
    
    def __str__(self):
        return self.period_name


class RevenueRecognitionLog(models.Model):
    """
    CRITICAL REFINEMENT: Track all revenue recognition events.
    Deferred revenue: Deposits recorded as liability, recognized when earned.
    Final revenue: Recognized only on final invoice.
    
    This log provides immutable audit trail of when revenue was recognized.
    """
    
    RECOGNITION_TYPE_CHOICES = [
        ('deposit_received', 'Deposit Received (Liability)'),
        ('interim_progress', 'Interim Progress Recognition'),
        ('final_revenue', 'Final Revenue Recognition'),
        ('direct_sale', 'Direct Sale Revenue'),
        ('rental_income', 'Rental Income'),
        ('reversal', 'Reversal Entry'),
    ]
    
    # Identification
    log_number = models.CharField(max_length=50, unique=True, db_index=True)
    recognition_date = models.DateField()
    recognition_type = models.CharField(max_length=30, choices=RECOGNITION_TYPE_CHOICES)
    
    # References
    invoice = models.ForeignKey(
        'sales.Invoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='revenue_recognitions'
    )
    contract = models.ForeignKey(
        'crm.Contract',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='revenue_recognitions'
    )
    
    # Amount & GL Accounts
    recognized_amount = models.DecimalField(max_digits=12, decimal_places=2)
    revenue_account = models.ForeignKey(
        ChartOfAccounts,
        on_delete=models.PROTECT,
        related_name='revenue_recognitions'
    )
    offset_account = models.ForeignKey(
        ChartOfAccounts,
        on_delete=models.PROTECT,
        related_name='revenue_offset_entries'
    )
    
    # GL Entry created
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revenue_recognitions'
    )
    
    # Audit
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Notes
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-recognition_date']
        indexes = [
            models.Index(fields=['log_number']),
            models.Index(fields=['recognition_date']),
            models.Index(fields=['invoice']),
            models.Index(fields=['contract']),
        ]
    
    def __str__(self):
        return f"{self.log_number} - {self.get_recognition_type_display()}: ${self.recognized_amount}"
    
    def save(self, *args, **kwargs):
        # Generate log_number if not set
        if not self.log_number:
            import uuid
            today = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4())[:6].upper()
            self.log_number = f"REV-{today}-{random_suffix}"
        
        super().save(*args, **kwargs)


class DeferredRevenueAccount(models.Model):
    """
    CRITICAL: Track deferred revenue by contract and recognition milestone.
    Deposits are recorded as liabilities here until earned/recognized.
    """
    
    # Reference
    contract = models.ForeignKey(
        'crm.Contract',
        on_delete=models.CASCADE,
        related_name='deferred_revenue'
    )
    invoice = models.ForeignKey(
        'sales.Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Amount
    deferred_amount = models.DecimalField(max_digits=12, decimal_places=2)
    recognized_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    recognized = models.BooleanField(default=False)
    recognized_at = models.DateField(null=True, blank=True)
    
    # Milestone
    milestone_description = models.CharField(max_length=255)
    milestone_date = models.DateField()
    
    # GL Accounts
    liability_account = models.ForeignKey(
        ChartOfAccounts,
        on_delete=models.PROTECT,
        related_name='deferred_revenue_liabilities'
    )
    revenue_account = models.ForeignKey(
        ChartOfAccounts,
        on_delete=models.PROTECT,
        related_name='deferred_revenue_recognitions'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['milestone_date']
        unique_together = ['contract', 'milestone_description']
    
    def __str__(self):
        return f"{self.contract.contract_number} - {self.milestone_description}: ${self.deferred_amount}"
    
    @property
    def balance(self):
        """Remaining deferred balance"""
        return self.deferred_amount - self.recognized_amount


class GLIntegrityCheck(models.Model):
    """
    REFINEMENT 4: Daily GL integrity verification
    
    Ensures:
    - All journal entries balance (debits = credits)
    - No orphaned GL postings
    - GL reconciliation trail for audit
    """
    
    # Reconciliation data
    check_date = models.DateField(auto_now_add=True, db_index=True)
    total_debits = models.DecimalField(max_digits=15, decimal_places=2)
    total_credits = models.DecimalField(max_digits=15, decimal_places=2)
    is_balanced = models.BooleanField(default=False)
    discrepancy = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Debits - Credits (should be 0)")
    
    # Audit trail
    performed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gl_integrity_checks'
    )
    notes = models.TextField(blank=True)
    
    # Metadata
    check_number = models.CharField(max_length=50, unique=True, db_index=True, editable=False)
    issues_found = models.IntegerField(default=0, help_text="Number of unbalanced entries found")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-check_date', '-created_at']
        indexes = [
            models.Index(fields=['-check_date']),
            models.Index(fields=['is_balanced']),
        ]
        verbose_name = "GL Integrity Check"
        verbose_name_plural = "GL Integrity Checks"
    
    def __str__(self):
        status = "✓ BALANCED" if self.is_balanced else f"✗ UNBALANCED (${self.discrepancy})"
        return f"GL Check {self.check_number} - {self.check_date} - {status}"
    
    def save(self, *args, **kwargs):
        # Auto-generate check_number if not set
        if not self.check_number:
            from datetime import datetime
            import uuid
            date_str = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:6].upper()
            self.check_number = f"GLK-{date_str}-{unique_id}"
        
        super().save(*args, **kwargs)
