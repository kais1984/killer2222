from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel


class ApprovalRule(BaseModel):
    """Define approval rules and workflows"""
    REQUEST_TYPE_CHOICES = [
        ('purchase_order', 'Purchase Order'),
        ('expense', 'Expense'),
        ('leave', 'Leave Request'),
        ('discount', 'Sales Discount'),
        ('credit_limit', 'Credit Limit'),
        ('payment', 'Payment'),
        ('other', 'Other'),
    ]
    
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.request_type} - {self.name}"


class ApprovalLevel(models.Model):
    """Approval levels in a workflow"""
    rule = models.ForeignKey(ApprovalRule, on_delete=models.CASCADE, related_name='levels')
    
    level = models.IntegerField(validators=[MinValueValidator(1)])
    
    approver_role = models.CharField(max_length=100)  # e.g., "Manager", "Finance Head"
    approver_name = models.CharField(max_length=255, blank=True)
    
    min_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    approval_time_limit_days = models.IntegerField(default=3)
    
    can_reject = models.BooleanField(default=True)
    can_request_changes = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['rule', 'level']
        ordering = ['rule', 'level']
    
    def __str__(self):
        return f"{self.rule.name} - Level {self.level}"


class ApprovalRequest(BaseModel):
    """Approval request tracking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('changes_requested', 'Changes Requested'),
        ('expired', 'Expired'),
    ]
    
    request_number = models.CharField(max_length=50, unique=True)
    rule = models.ForeignKey(ApprovalRule, on_delete=models.CASCADE, related_name='requests')
    
    requested_by = models.CharField(max_length=255)
    request_date = models.DateTimeField(auto_now_add=True)
    
    description = models.TextField()
    reference_number = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['status', '-request_date']),
        ]
    
    def __str__(self):
        return f"{self.request_number} - {self.status}"


class Approval(BaseModel):
    """Individual approval decision"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('changes_requested', 'Changes Requested'),
    ]
    
    request = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE, related_name='approvals')
    level = models.ForeignKey(ApprovalLevel, on_delete=models.CASCADE)
    
    approver = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    assigned_date = models.DateTimeField(auto_now_add=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    
    decision_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['request', 'level']
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.request.request_number} - Level {self.level.level}"


class AuditTrail(models.Model):
    """Audit trail for approvals"""
    request = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE, related_name='audit_trail')
    
    action = models.CharField(max_length=255)
    action_by = models.CharField(max_length=255)
    action_date = models.DateTimeField(auto_now_add=True)
    
    previous_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-action_date']
    
    def __str__(self):
        return f"{self.request.request_number} - {self.action}"
