"""
Rental Management Models: Rentals, returns, damage tracking
"""

from django.db import models
from django.core.validators import MinValueValidator
from inventory.models import Product
from crm.models import Client
from decimal import Decimal
from django.utils import timezone

class RentalAgreement(models.Model):
    """Dress rental agreements"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    rental_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='rentals')
    
    rental_date = models.DateField()
    return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Rental Charges
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_days = models.IntegerField(validators=[MinValueValidator(1)])
    rental_cost = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Deposit & Conditions
    security_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit_refunded = models.BooleanField(default=False)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Late Fees
    is_late = models.BooleanField(default=False)
    late_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Damage
    damage_reported = models.BooleanField(default=False)
    damage_description = models.TextField(blank=True)
    damage_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Total
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rental_date']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['return_date']),
        ]
    
    def __str__(self):
        return f"{self.rental_number} - {self.client.name}"
    
    def calculate_late_fee(self):
        """Calculate late fee if dress returned late"""
        if self.actual_return_date and self.actual_return_date > self.return_date:
            days_late = (self.actual_return_date - self.return_date).days
            # Late fee is 50% of daily rate per day
            return days_late * (self.daily_rate * Decimal('0.5'))
        return Decimal('0')
    
    def get_outstanding_amount(self):
        return self.total_amount - self.amount_paid


class RentalItem(models.Model):
    """Items in a rental agreement"""
    
    rental = models.ForeignKey(RentalAgreement, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - Rental {self.rental.rental_number}"


class RentalReturn(models.Model):
    """Track rental returns and condition"""
    
    CONDITION_CHOICES = [
        ('perfect', 'Perfect Condition'),
        ('minor_damage', 'Minor Damage'),
        ('major_damage', 'Major Damage'),
        ('lost', 'Lost'),
    ]
    
    rental = models.OneToOneField(RentalAgreement, on_delete=models.CASCADE, related_name='return_record')
    
    return_date = models.DateField()
    return_time = models.TimeField(blank=True, null=True)
    
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='perfect')
    damage_notes = models.TextField(blank=True)
    damage_photos = models.CharField(max_length=255, blank=True, null=True)
    
    cleaning_required = models.BooleanField(default=False)
    cleaning_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    returned_by = models.CharField(max_length=255, blank=True)
    received_by = models.CharField(max_length=255)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-return_date']
    
    def __str__(self):
        return f"Return {self.rental.rental_number}"


class RentalPayment(models.Model):
    """Rental payment tracking"""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('online', 'Online'),
    ]
    
    rental = models.ForeignKey(RentalAgreement, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment {self.reference_number} - {self.amount}"


class RentalInventory(models.Model):
    """Track availability of dresses for rental"""
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='rental_inventory')
    
    total_available = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    currently_rented = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    in_maintenance = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    damaged = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    average_daily_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_rental_days = models.IntegerField(default=0)
    total_rental_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Rental Inventory - {self.product.name}"
    
    def get_available_count(self):
        return self.total_available - self.currently_rented - self.in_maintenance - self.damaged
