"""
Inventory Management Models: Products, stock, locations, tracking
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

class Category(models.Model):
    """Product categories for luxury fashion items"""
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Collection(models.Model):
    """Fashion collection/season"""
    
    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter'),
    ]
    
    name = models.CharField(max_length=255)
    season = models.CharField(max_length=10, choices=SEASON_CHOICES)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    launch_date = models.DateField()
    image = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ['name', 'season', 'year']
        ordering = ['-year', '-launch_date']
    
    def __str__(self):
        return f"{self.name} {self.season.title()} {self.year}"


class Product(models.Model):
    """Product model for dresses, gowns, and custom pieces"""
    
    DRESS_TYPE_CHOICES = [
        ('wedding', 'Wedding Dress'),
        ('evening', 'Evening Gown'),
        ('cocktail', 'Cocktail Dress'),
        ('casual', 'Casual Dress'),
        ('custom', 'Custom Couture'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('sale', 'For Sale'),
        ('rental', 'For Rental'),
        ('both', 'Sale & Rental'),
    ]
    
    PRODUCT_TYPE_CHOICES = [
        ('ready_made', 'Ready-Made'),
        ('custom_made', 'Custom-Made'),
        ('rental_asset', 'Rental Asset'),
    ]
    
    SIZE_CHOICES = [
        ('XS', 'XS (0-2)'),
        ('S', 'S (2-4)'),
        ('M', 'M (6-8)'),
        ('L', 'L (10-12)'),
        ('XL', 'XL (14-16)'),
        ('XXL', 'XXL (18-20)'),
        ('custom', 'Custom Size'),
    ]
    
    COLOR_CHOICES = [
        ('white', 'White'),
        ('ivory', 'Ivory'),
        ('blush', 'Blush'),
        ('nude', 'Nude'),
        ('black', 'Black'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('custom', 'Custom'),
    ]
    
    # Basic Information
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    dress_type = models.CharField(max_length=20, choices=DRESS_TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='ready_made')
    
    # Physical Attributes
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    material = models.CharField(max_length=255, blank=True)
    
    # Inventory Control
    availability = models.CharField(max_length=10, choices=AVAILABILITY_CHOICES, default='both')
    quantity_in_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    quantity_available_for_rental = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    quantity_reserved = models.IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Reserved for rentals")
    quantity_on_order = models.IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Awaiting production")
    
    # Pricing
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    rental_price_per_day = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Images
    primary_image = models.CharField(max_length=255)
    gallery_images = models.ManyToManyField('ProductImage', blank=True, related_name='products')
    
    # Barcode
    barcode_number = models.CharField(max_length=100, unique=True, blank=True)
    barcode_image = models.CharField(max_length=255, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Audit Trail
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_created'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_updated'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['dress_type', 'availability']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
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
    
    def generate_barcode(self):
        """Barcode generation placeholder - implement with python-barcode if needed"""
        if not self.barcode_number:
            self.barcode_number = f"RF-{self.sku}"
        # Barcode generation requires python-barcode package
        # Install with: pip install python-barcode
    
    def get_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price == 0:
            return 0
        return ((self.sale_price - self.cost_price) / self.cost_price) * 100
    
    def is_low_stock(self, threshold=10):
        """Check if product is below low stock threshold"""
        return self.quantity_in_stock < threshold


class ProductImage(models.Model):
    """Product gallery images for wedding dress and evening gown photos"""
    
    image = models.ImageField(upload_to='products/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Product Image - {self.alt_text}" if self.alt_text else "Product Image"


class Warehouse(models.Model):
    """Storage locations for inventory"""
    
    LOCATION_TYPE_CHOICES = [
        ('atelier', 'Atelier'),
        ('showroom', 'Showroom'),
        ('warehouse', 'Warehouse'),
        ('storage', 'Storage'),
    ]
    
    name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES)
    address = models.TextField()
    city = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0, help_text="Maximum number of items")
    current_stock = models.IntegerField(default=0)
    manager = models.CharField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"
    
    def get_utilization_percentage(self):
        """Calculate warehouse utilization"""
        if self.capacity == 0:
            return 0
        return (self.current_stock / self.capacity) * 100


class StockLocation(models.Model):
    """Track inventory location and quantity"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_locations')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    
    quantity_available = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    quantity_reserved = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    quantity_damaged = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    last_counted = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'warehouse']
    
    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.name}"
    
    def get_available_quantity(self):
        return self.quantity_available - self.quantity_reserved


class StockMovement(models.Model):
    """
    CRITICAL REFINEMENT: Immutable audit trail of all inventory movements.
    Prevents negative stock, ensures no manual edits after creation.
    
    Every movement tied to a business event (sale, rental, return, etc)
    """
    
    MOVEMENT_TYPE_CHOICES = [
        ('purchase', 'Purchase Receipt'),
        ('sale', 'Sale'),
        ('rental', 'Rental'),
        ('return', 'Rental Return'),
        ('adjustment', 'Stock Adjustment'),
        ('damage', 'Damage/Loss'),
        ('transfer', 'Transfer Between Warehouses'),
    ]
    
    # Movement tracking
    movement_number = models.CharField(max_length=50, unique=True, db_index=True, editable=False, default='PENDING')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='outgoing_movements')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='incoming_movements')
    
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES, db_index=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Reference to business event
    reference_number = models.CharField(max_length=100, blank=True, db_index=True)
    reference_type = models.CharField(
        max_length=20,
        choices=[
            ('sale', 'Sale'),
            ('invoice', 'Invoice'),
            ('contract', 'Contract'),
            ('rental', 'Rental'),
            ('return', 'Return'),
        ],
        blank=True
    )
    
    # Balance tracking
    balance_before = models.IntegerField(default=0, help_text="Stock quantity before this movement")
    balance_after = models.IntegerField(default=0, help_text="Stock quantity after this movement")
    
    # Immutability controls
    is_locked = models.BooleanField(default=True, help_text="Locked after creation, prevents edits")
    locked_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    
    # Audit trail
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_movements_created'
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['movement_number']),
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['reference_number']),
        ]
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"
    
    def __str__(self):
        return f"Movement {self.movement_number} - {self.product.sku}"
    
    def save(self, *args, **kwargs):
        # Generate movement_number if not set
        if not self.movement_number:
            import uuid
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4())[:6].upper()
            self.movement_number = f"MOV-{today}-{random_suffix}"
        
        # Prevent editing locked movements
        if self.pk and self.is_locked:
            existing = StockMovement.objects.get(pk=self.pk)
            if existing.quantity != self.quantity or existing.movement_type != self.movement_type:
                raise ValidationError("Cannot edit locked stock movements")
        
        # Validate balance doesn't go negative
        if self.balance_after < 0:
            raise ValidationError(
                f"Stock movement would result in negative inventory: {self.product.sku}"
            )
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of locked movements"""
        if self.is_locked:
            raise ValidationError("Cannot delete locked stock movements. Create reversal instead.")
        super().delete(*args, **kwargs)


class RentalReservation(models.Model):
    """
    Track which products are reserved for which rentals.
    When contract is approved for rental, a reservation is created.
    """
    
    STATUS_CHOICES = [
        ('reserved', 'Reserved'),
        ('active', 'Active (Out with customer)'),
        ('returned', 'Returned'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rental_reservations')
    contract = models.ForeignKey('crm.Contract', on_delete=models.CASCADE, related_name='rental_reservations')
    quantity_reserved = models.IntegerField(validators=[MinValueValidator(1)])
    
    rental_start_date = models.DateField()
    rental_end_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reserved')
    
    returned_at = models.DateTimeField(null=True, blank=True)
    returned_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['product', 'contract']]
        ordering = ['rental_start_date']
        indexes = [
            models.Index(fields=['contract', 'status']),
            models.Index(fields=['product', 'rental_start_date', 'rental_end_date']),
        ]
    
    def __str__(self):
        return f"Reserve: {self.product.sku} ({self.quantity_reserved}) for {self.contract.contract_number}"


class LowStockAlert(models.Model):
    """Alert for low stock items"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    threshold = models.IntegerField()
    current_stock = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Alert: {self.product.sku} (Stock: {self.current_stock})"
