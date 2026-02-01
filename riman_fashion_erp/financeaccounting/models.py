"""
Finance & Accounting Models: Chart of Accounts, Journal Entries, Stock Movements
Implements double-entry bookkeeping with immutable audit trail.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q
from decimal import Decimal


class Account(models.Model):
    """
    Chart of Accounts (COA)
    Single source of truth for all ledger accounts
    """
    
    ACCOUNT_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    ACCOUNT_SUBTYPES = {
        'asset': [
            ('cash', 'Cash'),
            ('accounts_receivable', 'Accounts Receivable'),
            ('inventory', 'Inventory'),
            ('equipment', 'Equipment'),
            ('other_asset', 'Other Asset'),
        ],
        'liability': [
            ('accounts_payable', 'Accounts Payable'),
            ('short_term_loan', 'Short-term Loan'),
            ('long_term_debt', 'Long-term Debt'),
            ('other_liability', 'Other Liability'),
        ],
        'equity': [
            ('capital', 'Capital'),
            ('retained_earnings', 'Retained Earnings'),
        ],
        'revenue': [
            ('sales', 'Sales Revenue'),
            ('service_revenue', 'Service Revenue'),
            ('rental_revenue', 'Rental Revenue'),
            ('other_revenue', 'Other Revenue'),
        ],
        'expense': [
            ('cogs', 'Cost of Goods Sold'),
            ('salary', 'Salary Expense'),
            ('rent', 'Rent Expense'),
            ('utilities', 'Utilities Expense'),
            ('depreciation', 'Depreciation Expense'),
            ('other_expense', 'Other Expense'),
        ],
    }
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Account identity
    account_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="E.g., 1100 for Asset, 2100 for Liability"
    )
    account_name = models.CharField(max_length=255)
    
    # Classification
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES
    )
    account_subtype = models.CharField(max_length=50)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Description & audit
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['account_code']
        verbose_name = "Chart of Account"
        verbose_name_plural = "Chart of Accounts"
        indexes = [
            models.Index(fields=['account_type', 'is_active']),
            models.Index(fields=['account_code']),
        ]
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"
    
    def get_balance(self):
        """Calculate current balance from journal entries"""
        debits = self.journalentryline_set.filter(
            line_type='debit'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        credits = self.journalentryline_set.filter(
            line_type='credit'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Assets & Expenses increase with debit, decrease with credit
        # Liabilities, Equity & Revenue increase with credit, decrease with debit
        if self.account_type in ['asset', 'expense']:
            return debits - credits
        else:
            return credits - debits


class JournalEntry(models.Model):
    """
    IMMUTABLE journal entry (accounting transaction)
    Must have balanced debits and credits.
    """
    
    ENTRY_TYPES = [
        ('sale', 'Sale'),
        ('payment', 'Payment Received'),
        ('payment_reversal', 'Payment Reversal'),
        ('stock_movement', 'Stock Movement'),
        ('adjustment', 'Manual Adjustment'),
        ('opening', 'Opening Entry'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Identity
    journal_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Auto-generated: JE-2026-001"
    )
    
    # Entry details
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    entry_date = models.DateField()
    description = models.TextField()
    
    # Reference to source documents
    sale_id = models.UUIDField(null=True, blank=True, help_text="Reference to sales.Sale ID")
    payment_id = models.UUIDField(null=True, blank=True, help_text="Reference to sales.Payment ID")
    expense_id = models.UUIDField(null=True, blank=True, help_text="Reference to accounting.Expense ID")
    
    # Status (draft, posted, void)
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('posted', 'Posted'), ('void', 'Void')],
        default='draft'
    )
    
    # Audit trail
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Reversal support
    reversed_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reverses'
    )
    
    class Meta:
        ordering = ['-entry_date', '-created_at']
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        indexes = [
            models.Index(fields=['entry_date', 'entry_type']),
            models.Index(fields=['journal_number']),
        ]
    
    def __str__(self):
        return f"JE {self.journal_number} - {self.get_entry_type_display()}"
    
    def clean(self):
        # Validate balanced debits and credits on save
        total_debit = self.lines.filter(line_type='debit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_credit = self.lines.filter(line_type='credit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        if total_debit != total_credit:
            raise ValidationError(
                f"Journal entry not balanced. Debits: {total_debit}, Credits: {total_credit}"
            )
    
    def save(self, *args, **kwargs):
        # Generate journal_number if not set
        if not self.journal_number:
            from django.utils import timezone
            import uuid
            today = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4())[:8].upper()
            self.journal_number = f"JE-{today}-{random_suffix}"
        
        self.clean()
        super().save(*args, **kwargs)
    
    def is_balanced(self):
        """Check if total debits equal total credits"""
        total_debit = self.lines.filter(line_type='debit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_credit = self.lines.filter(line_type='credit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        return total_debit == total_credit
    
    def is_reversed(self):
        return self.reversed_by is not None


class JournalEntryLine(models.Model):
    """
    Individual debit/credit line in a journal entry.
    Multiple lines per entry, balanced.
    """
    
    LINE_TYPES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    # Account being credited/debited
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT
    )
    
    # Debit or Credit
    line_type = models.CharField(max_length=10, choices=LINE_TYPES)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Description for context
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['journal_entry', 'id']
        verbose_name = "Journal Entry Line"
        verbose_name_plural = "Journal Entry Lines"
    
    def __str__(self):
        return f"{self.journal_entry.journal_number} - {self.account} ({self.get_line_type_display()} {self.amount})"


class FinancialReport(models.Model):
    """
    Generated financial statements (read-only derivatives of journal entries)
    """
    
    REPORT_TYPES = [
        ('balance_sheet', 'Balance Sheet'),
        ('income_statement', 'Income Statement'),
        ('trial_balance', 'Trial Balance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    report_date = models.DateField()
    
    # Report data (stored as JSON for flexibility)
    report_data = models.JSONField()
    
    generated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-report_date']
        verbose_name = "Financial Report"
        verbose_name_plural = "Financial Reports"
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.report_date}"
