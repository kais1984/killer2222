"""
Supplier Management Models: Suppliers, purchases, cost tracking
"""

from django.db import models
from django.core.validators import MinValueValidator
from inventory.models import Product

class Supplier(models.Model):
    """Supplier profiles for fabrics, tailors, accessories, logistics"""
    
    CATEGORY_CHOICES = [
        ('fabric', 'Fabric Supplier'),
        ('tailor', 'Tailor/Production'),
        ('accessories', 'Accessories'),
        ('logistics', 'Logistics'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Contact Information
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Business Information
    tax_id = models.CharField(max_length=50, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    payment_terms = models.CharField(max_length=100, default='Net 30')
    
    # Rating & Performance
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0,
                                 validators=[MinValueValidator(0)])
    total_purchases = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def get_balance(self):
        """Calculate outstanding balance for supplier"""
        from django.db.models import Sum, Q
        
        invoices = PurchaseInvoice.objects.filter(supplier=self)
        total_amount = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_paid = invoices.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        return total_amount - total_paid


class PurchaseInvoice(models.Model):
    """Purchase invoice from suppliers"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('credit', 'Credit'),
    ]
    
    invoice_number = models.CharField(max_length=100, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice Details
    invoice_date = models.DateField()
    due_date = models.DateField()
    delivery_date = models.DateField(blank=True, null=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment Tracking
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    payment_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['supplier', 'status']),
            models.Index(fields=['invoice_date']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.supplier.name}"
    
    def get_outstanding_amount(self):
        return self.total_amount - self.amount_paid
    
    def update_status(self):
        """Auto-update invoice status based on payment"""
        if self.amount_paid == 0:
            self.status = 'draft'
        elif self.amount_paid < self.total_amount:
            self.status = 'partial'
        elif self.amount_paid >= self.total_amount:
            self.status = 'paid'


class PurchaseInvoiceItem(models.Model):
    """Line items in a purchase invoice"""
    
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=255)  # For non-product items like labor
    
    # Cost Breakdown
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    cost_type = models.CharField(max_length=50, choices=[
        ('fabric', 'Fabric'),
        ('labor', 'Labor'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ], default='fabric')
    
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.description} - {self.quantity}"


class SupplierPayment(models.Model):
    """Track supplier payments"""
    
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
    ])
    reference_number = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment {self.reference_number} - {self.amount}"

# ============= SUPPLIER PORTAL & PERFORMANCE MODELS =============

class SupplierPerformance(models.Model):
    """Track supplier performance metrics"""
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, related_name='performance')
    
    # Quality Metrics
    quality_score = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)  # Out of 5
    defect_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    
    # Delivery Metrics
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    average_delivery_days = models.IntegerField(default=0)
    
    # Price Metrics
    price_competitiveness_score = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)  # Out of 5
    
    # Communication
    responsiveness_score = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)  # Out of 5
    
    # Overall Rating
    overall_score = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)  # Out of 5
    
    last_review_date = models.DateField(null=True, blank=True)
    review_cycle_days = models.IntegerField(default=90)
    
    class Meta:
        verbose_name = 'Supplier Performance'
    
    def __str__(self):
        return f"Performance - {self.supplier.name}"


class PurchaseOrderTracking(models.Model):
    """Track purchase order status and delivery"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_production', 'In Production'),
        ('ready_to_ship', 'Ready to Ship'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    po_number = models.CharField(max_length=100, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    items_count = models.IntegerField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.po_number} - {self.supplier.name}"


class InvoiceMatching(models.Model):
    """PO vs Invoice matching and reconciliation"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('matched', 'Matched'),
        ('discrepancy', 'Discrepancy'),
        ('resolved', 'Resolved'),
    ]
    
    po = models.ForeignKey(PurchaseOrderTracking, on_delete=models.CASCADE, related_name='invoice_matches')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    
    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()
    invoice_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    po_amount = models.DecimalField(max_digits=15, decimal_places=2)
    matched_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    variance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    variance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    discrepancy_notes = models.TextField(blank=True)
    resolved_date = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ['po', 'invoice_number']
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - PO {self.po.po_number}"


class SupplierPaymentPortal(models.Model):
    """Portal configuration for supplier payments"""
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, related_name='payment_portal')
    
    portal_username = models.CharField(max_length=255, unique=True)
    portal_password = models.CharField(max_length=255)  # Should be encrypted
    
    is_portal_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    email_for_notifications = models.EmailField()
    notify_pending_payments = models.BooleanField(default=True)
    notify_invoice_receipt = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Supplier Payment Portal'
    
    def __str__(self):
        return f"Portal - {self.supplier.name}"


class SupplierDocument(models.Model):
    """Store supplier documents (certificates, contracts, etc)"""
    DOCUMENT_TYPE_CHOICES = [
        ('certificate', 'Certificate'),
        ('contract', 'Contract'),
        ('invoice', 'Invoice'),
        ('po_confirmation', 'PO Confirmation'),
        ('delivery_note', 'Delivery Note'),
        ('other', 'Other'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='documents')
    
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    document_name = models.CharField(max_length=255)
    document_file = models.FileField(upload_to='supplier_documents/')
    
    upload_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    is_verified = models.BooleanField(default=False)
    verified_by = models.CharField(max_length=255, blank=True)
    verified_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.supplier.name} - {self.document_name}"