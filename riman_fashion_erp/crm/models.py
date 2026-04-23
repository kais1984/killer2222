"""
CRM Models: Client management, measurements, appointments
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Client(models.Model):
    """Client profile with full transaction history"""
    
    CLIENT_TYPE_CHOICES = [
        ('walk_in', 'Walk-in Customer'),
        ('regular', 'Regular Customer'),
        ('vip', 'VIP Customer'),
        ('bridal', 'Bridal Client'),
        ('corporate', 'Corporate'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blacklisted', 'Blacklisted'),
    ]
    
    # Basic Information
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20)
    phone_2 = models.CharField(max_length=20, blank=True, null=True)
    
    # Client Classification
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES, default='regular')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Address Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Financial Information
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_rentals = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    general_notes = models.TextField(blank=True)
    preferences = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_purchase_date = models.DateField(blank=True, null=True)
    
    # Audit Trail
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_created'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_updated'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['client_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


class Measurement(models.Model):
    """Client measurements for custom tailoring"""
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='measurements')
    
    # Standard Measurements (in cm)
    bust = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    waist = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    hips = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    shoulder = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    sleeve_length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    dress_length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    # Additional Notes
    notes = models.TextField(blank=True)
    measured_by = models.CharField(max_length=255, blank=True)
    
    measured_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-measured_date']
    
    def __str__(self):
        return f"Measurements for {self.client.name}"


class Appointment(models.Model):
    """Client appointments for fittings and consultations"""
    
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('fitting', 'Fitting'),
        ('measurement', 'Measurement'),
        ('payment', 'Payment'),
        ('delivery', 'Delivery'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('no_show', 'No Show'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='appointments')
    
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    
    notes = models.TextField(blank=True)
    assigned_staff = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.get_appointment_type_display()} - {self.client.name} - {self.scheduled_date}"


class ClientNote(models.Model):
    """Follow-up notes and interaction records"""
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notes')
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    note_type = models.CharField(max_length=50, choices=[
        ('follow_up', 'Follow-up'),
        ('interaction', 'Interaction'),
        ('complaint', 'Complaint'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ], default='other')
    
    created_by = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client.name}"


class ClientPreference(models.Model):
    """Client style preferences and design preferences"""
    
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='preference')
    
    # Style Preferences
    preferred_styles = models.CharField(max_length=500, blank=True,
                                       help_text="Comma-separated list of preferred styles")
    favorite_colors = models.CharField(max_length=500, blank=True)
    favorite_designers = models.CharField(max_length=500, blank=True)
    
    # Fit Preferences
    preferred_fit = models.CharField(max_length=100, blank=True)
    preferred_neckline = models.CharField(max_length=100, blank=True)
    preferred_hemline = models.CharField(max_length=100, blank=True)
    preferred_sleeve_type = models.CharField(max_length=100, blank=True)
    
    # Fabric Preferences
    preferred_fabrics = models.CharField(max_length=500, blank=True)
    fabric_allergy = models.CharField(max_length=255, blank=True)
    
    # Budget
    typical_budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Preferences for {self.client.name}"


class ClientInteraction(models.Model):
    """Track all client interactions"""
    
    INTERACTION_TYPE_CHOICES = [
        ('phone', 'Phone Call'),
        ('email', 'Email'),
        ('in_person', 'In Person'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='interactions')
    
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    description = models.TextField()
    notes = models.TextField(blank=True)
    
    interaction_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-interaction_date']
    
    def __str__(self):
        return f"{self.get_interaction_type_display()} - {self.client.name}"


class Contract(models.Model):
    """
    MANDATORY contract system for Rentals, Custom Sales, and Custom Rentals.
    Pre-financial control document: revenue not recognized here.
    Immutable once invoicing begins.
    
    Status Lifecycle:
    Draft → Approved → (In Production for custom) → Ready → Completed
    """
    
    # Contract Type
    CONTRACT_TYPE_CHOICES = [
        ('rental', 'Rental'),
        ('custom_sale', 'Custom-Made for Sale'),
        ('custom_rent', 'Custom-Made for Rental'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('in_production', 'In Production'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Identification
    contract_number = models.CharField(max_length=50, unique=True, db_index=True)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    
    # Parties
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='contracts')
    sales_person = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts_sold'
    )
    
    # Product/Service Definition
    product_specification = models.TextField(help_text="Detailed description of product/service")
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts'
    )
    
    # Timeline
    contract_date = models.DateField()
    rental_start_date = models.DateField(null=True, blank=True)
    rental_end_date = models.DateField(null=True, blank=True)
    production_start_date = models.DateField(null=True, blank=True)
    production_end_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    
    # Design Specifications (CRITICAL for custom-made)
    design_notes = models.TextField(
        blank=True,
        help_text="Design specifications: style, silhouette, details, embellishments"
    )
    design_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reference to design sketch, inspiration, or template"
    )
    design_approved = models.BooleanField(default=False)
    design_approved_date = models.DateField(null=True, blank=True)
    
    # Measurements & Customization (CRITICAL for custom-made)
    measurements = models.JSONField(
        default=dict,
        help_text="{'bust': 92, 'waist': 78, 'hips': 98, 'length': 160}"
    )
    customization_details = models.TextField(
        blank=True,
        help_text="Specific alterations, fitting notes, custom requests"
    )
    
    # Fabric & Material Selection
    fabric_choice = models.CharField(max_length=255, blank=True)
    fabric_quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Quantity in meters"
    )
    color_choice = models.CharField(max_length=100, blank=True)
    
    # Pricing
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    deposit_due_date = models.DateField(null=True, blank=True)
    
    # Revenue Recognition Schedule (CRITICAL for GL)
    revenue_schedule = models.JSONField(
        default=list,
        help_text="[{'milestone': 'deposit', 'date': '2026-02-01', 'amount': 5000, 'description': 'Deposit - design'}]"
    )
    
    # Payment Schedule (Milestone-based)
    payment_schedule = models.JSONField(
        default=list,
        help_text="[{'date': '2026-02-01', 'amount': 5000, 'description': 'Milestone 1'}]"
    )
    
    # Rental-Specific Terms
    security_deposit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Security deposit for rental (refundable)"
    )
    late_return_penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Daily penalty for late return"
    )
    damage_liability = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Liability'),
            ('partial', 'Partial Liability'),
            ('full', 'Full Liability'),
        ],
        default='partial',
        help_text="Customer liability for damage"
    )
    damage_clause = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    
    # Immutability control
    invoicing_started_at = models.DateTimeField(null=True, blank=True)
    
    # Terms & Notes
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True, help_text="Custom contract terms")
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='contracts_created'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts_approved'
    )
    
    class Meta:
        ordering = ['-contract_date']
        indexes = [
            models.Index(fields=['contract_number']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['contract_type']),
        ]
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"
    
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
        # Import here to avoid circular imports
        from sales.models import Invoice
        invoiced_total = Invoice.objects.filter(
            contract=self,
            is_posted=True
        ).aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0')
        
        return self.total_price - invoiced_total
    
    def lock_for_invoicing(self):
        """Mark contract as invoicing started - becomes immutable"""
        from django.utils import timezone
        self.invoicing_started_at = timezone.now()
        self.save()
    
    def get_revenue_to_recognize(self, invoice_type):
        """
        CRITICAL: Determine revenue to recognize based on invoice type.
        Different for each sales type.
        """
        if invoice_type == 'deposit':
            return self.deposit_amount
        elif invoice_type == 'interim':
            return Decimal('0')  # No revenue on interim
        elif invoice_type == 'final':
            # Final invoice recognizes all remaining revenue
            return self.total_price - self.deposit_amount
        elif invoice_type == 'standard':
            return self.total_price
        return Decimal('0')
    
    def validate_revenue_schedule(self):
        """Ensure revenue schedule is valid and totals to contract amount"""
        total = sum(Decimal(str(item.get('amount', 0))) for item in self.revenue_schedule)
        if total != self.total_price:
            raise ValueError(
                f"Revenue schedule total ({total}) does not match contract amount ({self.total_price})"
            )
        return True
    
    def is_custom_made(self):
        """Check if contract is for custom-made product"""
        return self.contract_type in ['custom_sale', 'custom_rent']
    
    def needs_design_approval(self):
        """Custom-made contracts need design approval before production"""
        return self.is_custom_made() and not self.design_approved
    
    def approve_design(self, user):
        """Lock design and approve for production"""
        from django.utils import timezone
        if not self.is_custom_made():
            raise ValueError("Only custom-made contracts need design approval")
        self.design_approved = True
        self.design_approved_date = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        # Generate contract_number if not set
        if not self.contract_number:
            import uuid
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4())[:6].upper()
            self.contract_number = f"CNT-{today}-{random_suffix}"
        
        super().save(*args, **kwargs)
