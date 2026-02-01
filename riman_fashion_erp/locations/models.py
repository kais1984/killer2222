from django.db import models
from core.models import BaseModel


class Branch(BaseModel):
    """Branch/location management"""
    BRANCH_TYPE_CHOICES = [
        ('headquarters', 'Headquarters'),
        ('warehouse', 'Warehouse'),
        ('retail', 'Retail Store'),
        ('office', 'Office'),
        ('production', 'Production Facility'),
    ]
    
    branch_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    branch_type = models.CharField(max_length=50, choices=BRANCH_TYPE_CHOICES)
    
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    manager_name = models.CharField(max_length=255, blank=True)
    manager_phone = models.CharField(max_length=20, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.branch_code} - {self.name}"


class BranchInventory(models.Model):
    """Per-branch inventory tracking"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='inventory')
    
    product_code = models.CharField(max_length=100)  # Reference to Product
    product_name = models.CharField(max_length=255)
    
    quantity_on_hand = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0)
    
    last_stock_check = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ['branch', 'product_code']
    
    def __str__(self):
        return f"{self.branch.name} - {self.product_name}"


class InterBranchTransfer(BaseModel):
    """Stock transfer between branches"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    transfer_number = models.CharField(max_length=50, unique=True)
    
    from_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='incoming_transfers')
    
    requested_by = models.CharField(max_length=255)
    approved_by = models.CharField(max_length=255, blank=True)
    
    request_date = models.DateField(auto_now_add=True)
    approval_date = models.DateField(null=True, blank=True)
    ship_date = models.DateField(null=True, blank=True)
    receive_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.transfer_number} - {self.from_branch.name} to {self.to_branch.name}"


class TransferItem(models.Model):
    """Individual items in inter-branch transfer"""
    transfer = models.ForeignKey(InterBranchTransfer, on_delete=models.CASCADE, related_name='items')
    
    product_code = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    
    quantity_requested = models.IntegerField()
    quantity_sent = models.IntegerField(default=0)
    quantity_received = models.IntegerField(default=0)
    
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    class Meta:
        unique_together = ['transfer', 'product_code']
    
    def __str__(self):
        return f"{self.transfer.transfer_number} - {self.product_name}"


class BranchSales(BaseModel):
    """Sales statistics per branch"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='sales')
    
    period_date = models.DateField()
    
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_quantity = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['branch', 'period_date']
        ordering = ['-period_date']
    
    def __str__(self):
        return f"{self.branch.name} - {self.period_date}"


class BranchExpense(BaseModel):
    """Branch-specific expense tracking"""
    EXPENSE_CATEGORY_CHOICES = [
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('staff', 'Staff Salaries'),
        ('maintenance', 'Maintenance'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='expenses')
    
    category = models.CharField(max_length=50, choices=EXPENSE_CATEGORY_CHOICES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    expense_date = models.DateField()
    
    approved = models.BooleanField(default=False)
    approved_by = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-expense_date']
    
    def __str__(self):
        return f"{self.branch.name} - {self.category} - {self.amount}"
