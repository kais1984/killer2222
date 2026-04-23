from django.db import models
from django.core.validators import MinValueValidator
from inventory.models import Product, Warehouse
from crm.models import Client
from core.models import BaseModel


class WarehouseLocation(BaseModel):
    """Warehouse bin/shelf locations"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='locations')
    location_code = models.CharField(max_length=50)
    aisle = models.CharField(max_length=20)
    rack = models.CharField(max_length=20)
    level = models.CharField(max_length=20)
    bin = models.CharField(max_length=20)
    
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    current_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['warehouse', 'aisle', 'rack', 'level', 'bin']
        ordering = ['warehouse', 'aisle', 'rack', 'level', 'bin']
    
    def __str__(self):
        return f"{self.warehouse.name} - {self.location_code}"
    
    @property
    def available_capacity(self):
        return self.capacity - self.current_quantity


class StockAllocation(models.Model):
    """Track stock allocated to specific bins"""
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, related_name='allocations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='allocations')
    
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ['location', 'product']
    
    def __str__(self):
        return f"{self.product.name} @ {self.location.location_code}"


class Shipment(BaseModel):
    """Shipment/Order fulfillment tracking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed Delivery'),
        ('returned', 'Returned'),
    ]
    
    shipment_number = models.CharField(max_length=50, unique=True)
    sales_order = models.CharField(max_length=100, blank=True)  # Link to sales order
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_items = models.IntegerField(validators=[MinValueValidator(1)])
    packed_items = models.IntegerField(default=0)
    
    ship_date = models.DateField(null=True, blank=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    delivery_address = models.TextField()
    shipping_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.shipment_number} - {self.client.name if self.client else 'N/A'}"


class ShipmentItem(models.Model):
    """Individual items in a shipment"""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity_ordered = models.IntegerField(validators=[MinValueValidator(1)])
    quantity_packed = models.IntegerField(default=0)
    quantity_picked = models.IntegerField(default=0)
    
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        unique_together = ['shipment', 'product']
    
    def __str__(self):
        return f"{self.shipment.shipment_number} - {self.product.name}"


class ShippingCarrier(BaseModel):
    """Shipping carrier configuration"""
    CARRIER_CHOICES = [
        ('dhl', 'DHL'),
        ('fedex', 'FedEx'),
        ('ups', 'UPS'),
        ('local', 'Local Courier'),
        ('postal', 'Postal Service'),
    ]
    
    name = models.CharField(max_length=255)
    carrier_type = models.CharField(max_length=50, choices=CARRIER_CHOICES)
    
    tracking_url = models.URLField(blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ShipmentTracking(BaseModel):
    """Track shipment movement"""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking')
    carrier = models.ForeignKey(ShippingCarrier, on_delete=models.SET_NULL, null=True)
    
    tracking_number = models.CharField(max_length=100, unique=True)
    
    STATUS_CHOICES = [
        ('info_received', 'Info Received'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('exception', 'Exception'),
        ('returned', 'Returned'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    location = models.CharField(max_length=255, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-last_update']
    
    def __str__(self):
        return f"{self.tracking_number} - {self.shipment.shipment_number}"


class TrackingUpdate(models.Model):
    """Historical tracking updates"""
    tracking = models.ForeignKey(ShipmentTracking, on_delete=models.CASCADE, related_name='updates')
    
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.tracking.tracking_number} - {self.timestamp}"


class ReturnRequest(BaseModel):
    """Customer return/refund requests"""
    REASON_CHOICES = [
        ('defective', 'Defective Product'),
        ('wrong_item', 'Wrong Item Shipped'),
        ('changed_mind', 'Changed Mind'),
        ('not_as_described', 'Not as Described'),
        ('damaged', 'Damaged in Transit'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('inspected', 'Inspected'),
        ('processed', 'Processed'),
    ]
    
    return_number = models.CharField(max_length=50, unique=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='returns')
    
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField()
    
    items_returned = models.ManyToManyField(ShipmentItem)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    refund_processed_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.return_number} - {self.shipment.shipment_number}"


class PickingTask(BaseModel):
    """Warehouse picking task"""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    task_number = models.CharField(max_length=50, unique=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='picking_tasks')
    
    assigned_to = models.CharField(max_length=255)  # Warehouse staff
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    assigned_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['assigned_date']
    
    def __str__(self):
        return f"{self.task_number} - {self.shipment.shipment_number}"


class PackingTask(BaseModel):
    """Warehouse packing task"""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    task_number = models.CharField(max_length=50, unique=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='packing_tasks')
    
    assigned_to = models.CharField(max_length=255)  # Warehouse staff
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    assigned_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    box_number = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)  # e.g., "30x20x10cm"
    
    class Meta:
        ordering = ['assigned_date']
    
    def __str__(self):
        return f"{self.task_number} - {self.shipment.shipment_number}"
