"""
Sales Management Models: Sale, Invoice, Payment with Double-Entry Accounting
Core Flow: Sale → Invoice → Payment → Inventory Update → Accounting Entries
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from inventory.models import Product
from crm.models import Client


class Sale(models.Model):
    """
    ROOT TRUTH: Single authoritative sale record.
    Creates Invoice, Payments, StockMovements, and JournalEntries automatically.
    Status is DERIVED from payments, not manual.
    """
    
    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Auto-generated: SAL-2026-001"
    )
    
    # Core Reference
    customer = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='sales'
    )
    
    # Dates
    sale_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_created'
    )
    
    # Totals (CALCULATED from line items, immutable once invoiced)
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Sum of line items (read-only)"
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Tax calculated (read-only)"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Subtotal + Tax (read-only)"
    )
    
    # Cancellation (soft delete)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_cancelled'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-sale_date']
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        indexes = [
            models.Index(fields=['customer', '-sale_date']),
            models.Index(fields=['sale_number']),
            models.Index(fields=['-sale_date']),
        ]
    
    def __str__(self):
        return f"Sale {self.sale_number}"
    
    def save(self, *args, **kwargs):
        # Generate sale_number if not set
        if not self.sale_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4())[:8].upper()
            self.sale_number = f"SAL-{today}-{random_suffix}"
        
        # Prevent editing invoiced sales (only on update, not on create)
        if self.pk:
            try:
                existing = Sale.objects.get(pk=self.pk)
                if existing.invoice_set.exists():
                    raise ValidationError("Cannot modify sale after invoicing")
            except Sale.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    @property
    def total_paid(self):
        """Sum of all non-reversed payments"""
        total = self.payments.filter(reversed_by__isnull=True).aggregate(
            models.Sum('amount')
        )['amount__sum']
        return total or Decimal('0.00')
    
    @property
    def amount_due(self):
        """Outstanding balance"""
        return self.total_amount - self.total_paid
    
    @property
    def payment_status(self):
        """Derived from payments, not stored"""
        if self.total_paid == 0:
            return 'unpaid'
        elif self.total_paid < self.total_amount:
            return 'partial'
        else:
            return 'paid'
    
    @property
    def status(self):
        """Derived from cancellation and payments"""
        if self.cancelled_at:
            return 'cancelled'
        if not self.lines.exists():
            return 'draft'
        if self.payment_status == 'unpaid':
            return 'invoiced'
        return self.payment_status


class SaleLine(models.Model):
    """
    Line items on a sale.
    Immutable snapshot of product at time of sale.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    # Product & Quantity
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    
    # Unit price (immutable snapshot at time of sale)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Line total (calculated)
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="quantity * unit_price (read-only)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['sale', 'product']
        indexes = [
            models.Index(fields=['sale']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Recalculate line total
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """
    INVOICING SYSTEM: Supports multiple invoice types per contract.
    
    For Direct Sales: Single standard invoice
    For Contracts: Multiple invoices (deposit, interim, final)
    
    Immutable once posted.
    Status derived from payments.
    Revenue recognition on final invoice.
    """
    
    INVOICE_TYPE_CHOICES = [
        ('standard', 'Standard Invoice'),
        ('deposit', 'Deposit Invoice'),
        ('interim', 'Interim Invoice'),
        ('final', 'Final Invoice'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True
    )
    
    # Source (one required: sale OR contract)
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='invoices'
    )
    contract = models.ForeignKey(
        'crm.Contract',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='invoices'
    )
    
    # Invoice Type (only matters for contracts)
    invoice_type = models.CharField(
        max_length=20,
        choices=INVOICE_TYPE_CHOICES,
        default='standard'
    )
    
    # Dates
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Immutable totals (snapshot)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Posting (immutability control)
    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_posted'
    )
    
    # GL posting
    gl_posted = models.BooleanField(default=False, help_text="Revenue recognized in GL")
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_created'
    )
    
    class Meta:
        ordering = ['-invoice_date']
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['-invoice_date']),
            models.Index(fields=['contract', 'invoice_type']),
        ]
        unique_together = [
            ('contract', 'invoice_type'),  # One of each type per contract
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    # DERIVED PROPERTIES
    @property
    def amount_paid(self):
        """Sum of all non-reversed payments"""
        total = self.payment_set.filter(reversed_at__isnull=True).aggregate(
            models.Sum('amount')
        )['amount__sum']
        return total or Decimal('0.00')
    
    @property
    def amount_due(self):
        """Outstanding balance"""
        return self.total_amount - self.amount_paid
    
    @property
    def status(self):
        """Derived from payments"""
        if self.amount_paid == 0:
            return 'unpaid'
        elif self.amount_paid < self.total_amount:
            return 'partial'
        else:
            return 'paid'
    
    # BUSINESS RULES
    def can_edit(self):
        """Cannot edit posted invoices"""
        return not self.is_posted
    
    def can_delete(self):
        """Cannot delete posted invoices"""
        return not self.is_posted
    
    def post_to_gl(self):
        """Create GL entries for revenue recognition"""
        if self.is_posted:
            raise ValidationError("Invoice already posted to GL")
        
        from django.utils import timezone
        from financeaccounting.services import SaleAccountingService
        
        # Use accounting service to post
        service = SaleAccountingService()
        
        if self.sale:
            service.post_sale_invoice(self)
        elif self.contract:
            service.post_contract_invoice(self)
        
        self.is_posted = True
        self.posted_at = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        # Validate source
        if not self.sale and not self.contract:
            raise ValidationError("Invoice must have Sale OR Contract")
        
        if self.sale and self.contract:
            raise ValidationError("Invoice cannot have both Sale and Contract")
        
        # Generate invoice_number if not set
        if not self.invoice_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4())[:8].upper()
            self.invoice_number = f"INV-{today}-{random_suffix}"
        
        # Track if this is a new invoice
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Generate accounting entries for new invoice
        if is_new and self.sale:
            try:
                from financeaccounting.services import SaleAccountingService
                
                # Post revenue recognition entry
                SaleAccountingService.post_invoice(self)
                
                # Post COGS and inventory reduction for each line item
                for line in self.sale.lines.all():
                    SaleAccountingService.post_stock_movement(line)
                    
            except Exception as e:
                # Log error but don't fail invoice creation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create accounting entries for Invoice {self.invoice_number}: {str(e)}")

    
    @property
    def amount_paid(self):
        """Derived from related payments"""
        return self.sale.total_paid
    
    @property
    def amount_due(self):
        return self.total_amount - self.amount_paid
    
    @property
    def status(self):
        """Derived from payments"""
        if self.amount_paid == 0:
            return 'unpaid'
        elif self.amount_paid < self.total_amount:
            return 'partial'
        else:
            return 'paid'


class Payment(models.Model):
    """
    IMMUTABLE payment record.
    Never edited - only reversed via Payment reversal.
    Creates double-entry accounting automatically.
    """
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('cash_deposit', 'Cash Deposit'),
        ('atm_cash', 'ATM Cash'),
        ('pos', 'POS'),
        ('card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('stripe', 'Stripe'),
        ('wise', 'Wise'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        null=True,
        blank=True
    )
    
    # Reference
    sale = models.ForeignKey(
        Sale,
        on_delete=models.PROTECT,
        related_name='payments',
        null=True,
        blank=True
    )
    
    # Amount
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Method
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Check#, Auth code, Transfer reference, etc."
    )
    
    # Dates
    payment_date = models.DateField()
    recorded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_created'
    )
    notes = models.TextField(blank=True)
    
    # Reversal (for refunds/corrections)
    reversed_by = models.OneToOneField(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reverses'
    )
    
    class Meta:
        ordering = ['-payment_date', '-recorded_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [
            models.Index(fields=['sale', '-payment_date']),
            models.Index(fields=['payment_number']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_number}: {self.amount}"
    
    def clean(self):
        # Prevent overpayment
        if self.amount and self.sale:
            amount_paid = self.sale.payments.filter(reversed_by__isnull=True).exclude(
                id=self.id
            ).aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            if (amount_paid + self.amount) > self.sale.total_amount:
                raise ValidationError(
                    f"Payment {self.amount} exceeds amount due "
                    f"{self.sale.amount_due}"
                )
        
        # Prevent negative/zero payments
        if self.amount and self.amount <= 0:
            raise ValidationError("Payment amount must be positive")
    
    def save(self, *args, **kwargs):
        # Generate payment_number if not set
        if not self.payment_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4())[:8].upper()
            self.payment_number = f"PAY-{today}-{random_suffix}"
        
        # Track if this is a new payment
        is_new = self.pk is None
        
        self.clean()
        super().save(*args, **kwargs)
        
        # Generate accounting entry for new payment
        if is_new and self.sale:
            try:
                from financeaccounting.services import SaleAccountingService
                SaleAccountingService.post_payment(self)
                    
            except Exception as e:
                # Log error but don't fail payment creation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create accounting entry for Payment {self.payment_number}: {str(e)}")

    
    def is_reversed(self):
        return self.reversed_by is not None


class Promotion(models.Model):
    """Sales promotions and discounts"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
    ]
    
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    applicable_products = models.ManyToManyField(Product, blank=True)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    max_uses = models.IntegerField(blank=True, null=True)
    current_uses = models.IntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def calculate_discount(self, amount):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            return (amount * self.discount_value) / 100
        else:
            return self.discount_value


class CustomOrder(models.Model):
    """Custom couture orders - for future rental/appointment system"""
    
    STATUS_CHOICES = [
        ('inquiry', 'Inquiry'),
        ('consultation', 'Consultation'),
        ('design', 'Design Phase'),
        ('approved', 'Design Approved'),
        ('production', 'In Production'),
        ('fitting', 'Fitting'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='custom_orders')
    
    specifications = models.TextField()
    design_sketch = models.CharField(max_length=255, blank=True, null=True)
    
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    final_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    expected_completion_date = models.DateField()
    actual_completion_date = models.DateField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inquiry')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Custom Order {self.order_number}"
