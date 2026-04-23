from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from inventory.models import Product
from production.models import WorkOrder, WorkOrderStage
from core.models import BaseModel


class QualityChecklistTemplate(BaseModel):
    """Quality inspection checklist templates"""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='quality_templates')
    description = models.TextField(blank=True)
    inspection_stage = models.CharField(max_length=50, choices=[
        ('incoming', 'Incoming Materials'),
        ('in_process', 'In-Process'),
        ('final', 'Final Inspection'),
    ])
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ChecklistItem(models.Model):
    """Individual checklist items"""
    template = models.ForeignKey(QualityChecklistTemplate, on_delete=models.CASCADE, related_name='items')
    sequence = models.IntegerField()
    parameter = models.CharField(max_length=255)  # e.g., "Fabric Color", "Seam Quality"
    specification = models.TextField()  # e.g., "Color should match reference sample"
    acceptance_criteria = models.TextField()
    check_type = models.CharField(max_length=20, choices=[
        ('visual', 'Visual'),
        ('measurement', 'Measurement'),
        ('functional', 'Functional'),
        ('destructive', 'Destructive'),
    ])
    
    class Meta:
        ordering = ['sequence']
    
    def __str__(self):
        return f"{self.template.code} - {self.parameter}"


class InspectionRecord(BaseModel):
    """Quality inspection records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    ]
    
    inspection_number = models.CharField(max_length=50, unique=True)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='inspections')
    stage = models.ForeignKey(WorkOrderStage, on_delete=models.SET_NULL, null=True, blank=True)
    
    template = models.ForeignKey(QualityChecklistTemplate, on_delete=models.SET_NULL, null=True)
    
    inspector_name = models.CharField(max_length=255)
    inspection_date = models.DateTimeField()
    
    units_inspected = models.IntegerField(validators=[MinValueValidator(1)])
    units_passed = models.IntegerField(default=0)
    units_failed = models.IntegerField(default=0)
    units_rework = models.IntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.inspection_number} - {self.work_order.wo_number}"
    
    @property
    def pass_rate(self):
        if self.units_inspected > 0:
            return (self.units_passed / self.units_inspected) * 100
        return 0


class InspectionChecklistResult(models.Model):
    """Results for individual checklist items"""
    RESULT_CHOICES = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional Pass'),
    ]
    
    inspection = models.ForeignKey(InspectionRecord, on_delete=models.CASCADE, related_name='results')
    checklist_item = models.ForeignKey(ChecklistItem, on_delete=models.CASCADE)
    
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    actual_value = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.inspection.inspection_number} - {self.checklist_item.parameter}"


class DefectLog(BaseModel):
    """Log detected defects"""
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
    ]
    
    DEFECT_CATEGORIES = [
        ('color', 'Color Issue'),
        ('seam_quality', 'Seam Quality'),
        ('measurement', 'Measurement'),
        ('fabric_defect', 'Fabric Defect'),
        ('stitch_defect', 'Stitch Defect'),
        ('trim', 'Trim Issue'),
        ('finish', 'Finish Issue'),
        ('other', 'Other'),
    ]
    
    defect_number = models.CharField(max_length=50, unique=True)
    inspection = models.ForeignKey(InspectionRecord, on_delete=models.CASCADE, related_name='defects')
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='defects')
    
    category = models.CharField(max_length=50, choices=DEFECT_CATEGORIES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    
    root_cause = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    action_taken_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('under_investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], default='open')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.defect_number} - {self.severity}"


class QualityMetrics(BaseModel):
    """Overall quality metrics and statistics"""
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_date = models.DateField()
    
    total_inspections = models.IntegerField(default=0)
    total_units_inspected = models.IntegerField(default=0)
    total_units_passed = models.IntegerField(default=0)
    total_defects = models.IntegerField(default=0)
    
    critical_defects = models.IntegerField(default=0)
    major_defects = models.IntegerField(default=0)
    minor_defects = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-period_date']
        unique_together = ['period', 'period_date']
    
    def __str__(self):
        return f"{self.period.title()} - {self.period_date}"
    
    @property
    def overall_pass_rate(self):
        if self.total_units_inspected > 0:
            return (self.total_units_passed / self.total_units_inspected) * 100
        return 0
    
    @property
    def defect_rate(self):
        if self.total_units_inspected > 0:
            return (self.total_defects / self.total_units_inspected) * 100
        return 0


class ComplianceChecklist(BaseModel):
    """Compliance standards and tracking"""
    name = models.CharField(max_length=255)
    standard = models.CharField(max_length=100)  # e.g., "ISO 9001", "ASTM D 6193"
    description = models.TextField(blank=True)
    
    is_mandatory = models.BooleanField(default=True)
    last_audit_date = models.DateField(null=True, blank=True)
    next_audit_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.standard} - {self.name}"
