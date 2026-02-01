from django.db import models
from core.models import BaseModel


class BarcodeTemplate(BaseModel):
    """Barcode template configuration"""
    BARCODE_FORMAT_CHOICES = [
        ('code128', 'Code 128'),
        ('code39', 'Code 39'),
        ('ean13', 'EAN-13'),
        ('ean8', 'EAN-8'),
        ('upca', 'UPC-A'),
        ('qrcode', 'QR Code'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    barcode_format = models.CharField(max_length=50, choices=BARCODE_FORMAT_CHOICES)
    
    width_mm = models.IntegerField(default=50)
    height_mm = models.IntegerField(default=30)
    
    include_product_name = models.BooleanField(default=True)
    include_price = models.BooleanField(default=False)
    include_date = models.BooleanField(default=False)
    
    font_size = models.IntegerField(default=12)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ProductBarcode(BaseModel):
    """Product barcode records"""
    product_code = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    
    barcode = models.CharField(max_length=100, unique=True)
    barcode_format = models.CharField(max_length=50)
    
    template = models.ForeignKey(BarcodeTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['product_code', 'barcode_format']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product_name} - {self.barcode}"


class ProductBatch(BaseModel):
    """Track product batches with batch numbers"""
    batch_number = models.CharField(max_length=50, unique=True)
    product_code = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    
    manufacture_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    
    quantity = models.IntegerField()
    warehouse_location = models.CharField(max_length=255, blank=True)
    
    quality_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending Inspection'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.batch_number} - {self.product_name}"


class ProductSerial(BaseModel):
    """Track serial numbers for high-value items"""
    serial_number = models.CharField(max_length=100, unique=True)
    product_code = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    
    batch = models.ForeignKey(ProductBatch, on_delete=models.SET_NULL, null=True, blank=True, related_name='serials')
    
    manufacture_date = models.DateField()
    
    status = models.CharField(max_length=50, choices=[
        ('in_stock', 'In Stock'),
        ('sold', 'Sold'),
        ('returned', 'Returned'),
        ('damaged', 'Damaged'),
    ], default='in_stock')
    
    customer_reference = models.CharField(max_length=100, blank=True)  # Invoice/Order reference
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.serial_number} - {self.product_name}"


class BarcodeLabel(BaseModel):
    """Barcode label printing records"""
    label_number = models.CharField(max_length=50, unique=True)
    
    product_barcode = models.ForeignKey(ProductBarcode, on_delete=models.CASCADE)
    
    batch_size = models.IntegerField(default=100, help_text="Number of labels in print batch")
    
    print_date = models.DateField(auto_now_add=True)
    printed_by = models.CharField(max_length=255)
    
    quantity_printed = models.IntegerField()
    quantity_used = models.IntegerField(default=0)
    quantity_wasted = models.IntegerField(default=0)
    
    template_used = models.ForeignKey(BarcodeTemplate, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-print_date']
    
    def __str__(self):
        return f"{self.label_number} - {self.product_barcode.product_name}"


class BarcodeScan(models.Model):
    """Record of barcode scans for tracking"""
    barcode = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    
    scan_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)
    
    scan_action = models.CharField(max_length=100, choices=[
        ('receive', 'Receive'),
        ('pick', 'Pick'),
        ('pack', 'Pack'),
        ('ship', 'Ship'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('inventory_check', 'Inventory Check'),
    ])
    
    scanned_by = models.CharField(max_length=255)
    
    class Meta:
        ordering = ['-scan_date']
        indexes = [
            models.Index(fields=['barcode', '-scan_date']),
        ]
    
    def __str__(self):
        return f"{self.barcode} - {self.scan_action}"
