from django.db import models
from django.core.validators import MinValueValidator
from inventory.models import Product, Warehouse
from core.models import BaseModel


class BillOfMaterials(BaseModel):
    """Bill of Materials - defines components for a product"""
    code = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bill of Materials'
        verbose_name_plural = 'Bills of Materials'
    
    def __str__(self):
        return f"{self.code} - {self.product.name}"


class BOMComponent(models.Model):
    """Individual components in a Bill of Materials"""
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('m', 'Meter'),
        ('cm', 'Centimeter'),
        ('unit', 'Unit'),
        ('box', 'Box'),
        ('roll', 'Roll'),
    ]
    
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE, related_name='components')
    component = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom_components')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='unit')
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    waste_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    sequence = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['sequence']
    
    def __str__(self):
        return f"{self.bom.code} - {self.component.name}"
    
    @property
    def total_cost(self):
        return self.quantity * self.cost_per_unit * (1 + self.waste_percentage / 100)


class ProductionStage(models.Model):
    """Define production stages in the manufacturing process"""
    STAGE_CHOICES = [
        ('cutting', 'Cutting'),
        ('stitching', 'Stitching'),
        ('embroidery', 'Embroidery'),
        ('dyeing', 'Dyeing'),
        ('pressing', 'Pressing'),
        ('inspection', 'Inspection'),
        ('packaging', 'Packaging'),
        ('quality_check', 'Quality Check'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    stage_type = models.CharField(max_length=50, choices=STAGE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=100)
    estimated_duration_hours = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    sequence = models.IntegerField(default=0)
    required_equipment = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['sequence']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class WorkOrder(BaseModel):
    """Work Order - Production task for a batch of items"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    wo_number = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='work_orders')
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.SET_NULL, null=True, related_name='work_orders')
    order_reference = models.CharField(max_length=100, blank=True)  # Link to sales order
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.IntegerField(default=0, help_text="Higher = higher priority")
    
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    target_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wo_number} - {self.product.name}"
    
    @property
    def total_cost(self):
        return self.quantity * self.unit_cost
    
    @property
    def progress_percentage(self):
        if not self.stages.exists():
            return 0
        completed = self.stages.filter(status='completed').count()
        total = self.stages.count()
        return (completed / total * 100) if total > 0 else 0


class WorkOrderStage(models.Model):
    """Track production stages within a work order"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('failed', 'Failed'),
    ]
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='stages')
    stage = models.ForeignKey(ProductionStage, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sequence = models.IntegerField()
    
    assigned_to = models.CharField(max_length=255, blank=True)  # Department/Team
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    units_completed = models.IntegerField(default=0)
    units_failed = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['sequence']
        unique_together = ['work_order', 'stage']
    
    def __str__(self):
        return f"{self.work_order.wo_number} - {self.stage.name}"


class LaborCostAllocation(BaseModel):
    """Allocate labor costs to work orders"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='labor_costs')
    stage = models.ForeignKey(WorkOrderStage, on_delete=models.CASCADE)
    
    employee_name = models.CharField(max_length=255)
    hours_worked = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    task_description = models.TextField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.work_order.wo_number} - {self.employee_name}"
    
    @property
    def total_cost(self):
        return self.hours_worked * self.hourly_rate


class ProductionMetrics(BaseModel):
    """Track production metrics and KPIs"""
    work_order = models.OneToOneField(WorkOrder, on_delete=models.CASCADE, related_name='metrics')
    
    total_units_produced = models.IntegerField(default=0)
    units_accepted = models.IntegerField(default=0)
    units_rejected = models.IntegerField(default=0)
    units_rework = models.IntegerField(default=0)
    
    yield_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    production_time_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overhead_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Metrics - {self.work_order.wo_number}"
    
    @property
    def total_production_cost(self):
        return self.material_cost + self.labor_cost + self.overhead_cost
    
    @property
    def cost_per_unit(self):
        if self.units_accepted > 0:
            return self.total_production_cost / self.units_accepted
        return 0
