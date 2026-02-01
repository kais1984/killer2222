"""
Core Models: User management, roles, permissions, company settings
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

class User(AbstractUser):
    """Extended User model with role-based access control"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('accountant', 'Accountant'),
        ('sales', 'Sales Staff'),
        ('inventory', 'Inventory Manager'),
        ('manager', 'Manager'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        swappable = 'AUTH_USER_MODEL'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        if self.is_superuser:
            return True
        
        role_permissions = {
            'admin': ['view_all', 'edit_all', 'delete_all', 'approve_all'],
            'accountant': ['view_financial', 'edit_financial', 'view_reports'],
            'sales': ['view_sales', 'create_sales', 'edit_sales', 'view_customers'],
            'inventory': ['view_inventory', 'edit_inventory', 'manage_stock'],
            'manager': ['view_all', 'edit_all', 'view_reports'],
        }
        
        return permission in role_permissions.get(self.role, [])


class CompanySettings(models.Model):
    """Company profile and settings for RIMAN FASHION"""
    
    TAX_TYPE_CHOICES = [
        ('vat', 'VAT'),
        ('gst', 'GST'),
        ('sales_tax', 'Sales Tax'),
        ('none', 'No Tax'),
    ]
    
    company_name = models.CharField(max_length=255, default='RIMAN FASHION')
    company_slug = models.SlugField(unique=True, default='riman-fashion')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, help_text='Company logo (recommended size: 200x100px)')
    brand_color = models.CharField(max_length=7, default='#2c3e50')
    accent_color = models.CharField(max_length=7, default='#e74c3c')
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Financial Settings
    currency_symbol = models.CharField(max_length=5, default='$')
    currency_code = models.CharField(max_length=3, default='USD')
    tax_type = models.CharField(max_length=20, choices=TAX_TYPE_CHOICES, default='vat')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                    validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Invoice Settings
    invoice_prefix = models.CharField(max_length=10, default='INV-')
    invoice_next_number = models.IntegerField(default=1000)
    invoice_footer = models.TextField(blank=True)
    
    # System Settings
    financial_year_start = models.CharField(max_length=5, default='01-01')  # MM-DD format
    low_stock_threshold = models.IntegerField(default=10)

    # Document Upload Settings
    upload_max_size = models.BigIntegerField(default=5 * 1024 * 1024, help_text='Maximum upload size in bytes for document templates')
    allowed_extensions = models.CharField(max_length=255, default='pdf,docx,doc,xlsx,xls,html,txt', help_text='Comma separated list of allowed file extensions')
    enforce_mime = models.BooleanField(default=True, help_text='Enforce content-based MIME/type checking on uploads')
    use_s3 = models.BooleanField(default=False, help_text='When enabled, documents are expected to use remote storage (S3)')
    virus_scan = models.BooleanField(default=False, help_text='Enable virus scanning (requires ClamAV/clamd)')
    # When enabled, infected uploads will be automatically quarantined (disabled)
    auto_quarantine = models.BooleanField(default=True, help_text='Automatically quarantine (deactivate) infected document templates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'
    
    def __str__(self):
        return self.company_name


class AuditLog(models.Model):
    """Track all system changes for audit and compliance"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    description = models.TextField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"


class Notification(models.Model):
    """System notifications for users"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
