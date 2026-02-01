"""
Document Templates Management Models
Manages templates for invoices, contracts, and other business documents
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class DocumentTemplate(models.Model):
    """Base template model for all document types"""
    
    TEMPLATE_TYPES = [
        ('invoice', 'Invoice Template'),
        ('contract', 'Contract Template'),
        ('receipt', 'Receipt Template'),
        ('purchase_order', 'Purchase Order Template'),
        ('delivery_note', 'Delivery Note Template'),
    ]
    
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('doc', 'Word Document'),
        ('xlsx', 'Excel'),
        ('xls', 'Excel'),
        ('html', 'HTML'),
        ('txt', 'Text'),
        ('other', 'Other'),
    ]
    
    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, db_index=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    # Content
    description = models.TextField(blank=True)
    content = models.TextField(help_text="HTML/Template content", blank=True)
    template_file = models.FileField(
        upload_to='templates/files/',
        null=True,
        blank=True,
        help_text="Upload your invoice/contract file (PDF, Word, etc.)"
    )
    preview_image = models.ImageField(upload_to='templates/previews/', null=True, blank=True)
    file_type = models.CharField(
        max_length=20,
        choices=[
            ('pdf', 'PDF'),
            ('docx', 'Word Document'),
            ('doc', 'Word Document'),
            ('xlsx', 'Excel'),
            ('xls', 'Excel'),
            ('html', 'HTML'),
            ('txt', 'Text'),
            ('other', 'Other'),
        ],
        default='pdf',
        blank=True
    )
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['is_default', 'template_type']),
        ]
        verbose_name = 'Document Template'
        verbose_name_plural = 'Document Templates'
    
    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_default = models.BooleanField(default=False)

    # Scan status for uploaded templates
    SCAN_STATUS_CHOICES = [
        ('unknown', 'Unknown'),
        ('pending', 'Pending'),
        ('clean', 'Clean'),
        ('infected', 'Infected'),
        ('error', 'Error')
    ]
    scan_status = models.CharField(
        max_length=20,
        choices=SCAN_STATUS_CHOICES,
        default='unknown',
        help_text='Current virus scan status for uploaded template files',
        db_index=True
    )

    # Reason recorded when template got quarantined (infected)
    quarantine_reason = models.TextField(blank=True, help_text='Reason or message recorded when the template was quarantined (e.g., scan result)')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='templates_created'
    )
    
    # Version control
    version = models.PositiveIntegerField(default=1)
    parent_template = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['is_default', 'template_type']),
        ]
    
    def __str__(self):
        return f"{self.get_template_type_display()} - {self.name}"
    
    def set_as_default(self):
        """Set this template as default for its type"""
        # Unset other defaults of same type
        DocumentTemplate.objects.filter(
            template_type=self.template_type,
            is_default=True
        ).exclude(id=self.id).update(is_default=False)
        
        self.is_default = True
        self.save()


class InvoiceTemplate(models.Model):
    """Specialized invoice template with field mappings"""
    
    # Link to document template
    template = models.OneToOneField(
        DocumentTemplate,
        on_delete=models.CASCADE,
        related_name='invoice_template'
    )
    
    # Invoice configuration
    invoice_prefix = models.CharField(max_length=10, default='INV-')
    invoice_number_format = models.CharField(
        max_length=50,
        default='{prefix}{year}-{sequence}',
        help_text="Format: {prefix}{year}-{sequence}"
    )
    
    # Fields configuration
    show_po_number = models.BooleanField(default=True)
    show_tax = models.BooleanField(default=True)
    show_discount = models.BooleanField(default=True)
    show_notes = models.BooleanField(default=True)
    show_terms = models.BooleanField(default=True)
    
    # Styling
    company_logo_position = models.CharField(
        max_length=20,
        choices=[('top_left', 'Top Left'), ('top_right', 'Top Right'), ('hidden', 'Hidden')],
        default='top_left'
    )
    color_scheme = models.CharField(max_length=50, default='blue', help_text="Primary color theme")
    font_family = models.CharField(max_length=50, default='Arial', help_text="Base font for template")
    
    # Payment terms
    payment_terms_text = models.TextField(
        default="Net 30",
        help_text="Default payment terms text"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Invoice Template"
        verbose_name_plural = "Invoice Templates"
    
    def __str__(self):
        return f"Invoice Template: {self.template.name}"


class ContractTemplate(models.Model):
    """Specialized contract template with clause management"""
    
    # Link to document template
    template = models.OneToOneField(
        DocumentTemplate,
        on_delete=models.CASCADE,
        related_name='contract_template'
    )
    
    # Contract configuration
    contract_type = models.CharField(
        max_length=50,
        choices=[
            ('master_service', 'Master Service Agreement'),
            ('rental', 'Rental Agreement'),
            ('custom_design', 'Custom Design Agreement'),
            ('supplier', 'Supplier Agreement'),
            ('employment', 'Employment Contract'),
        ],
        default='master_service'
    )
    
    # Clauses (JSON-like structure)
    includes_payment_terms = models.BooleanField(default=True)
    includes_liability = models.BooleanField(default=True)
    includes_confidentiality = models.BooleanField(default=True)
    includes_termination = models.BooleanField(default=True)
    includes_dispute_resolution = models.BooleanField(default=True)
    
    # Customization
    company_name_required = models.BooleanField(default=True)
    client_name_required = models.BooleanField(default=True)
    date_fields_required = models.BooleanField(default=True)
    amount_fields_required = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contract Template"
        verbose_name_plural = "Contract Templates"
    
    def __str__(self):
        return f"Contract Template: {self.template.name}"


class TemplateScanLog(models.Model):
    """Record scan events for templates"""
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.CASCADE,
        related_name='scan_logs'
    )
    result = models.CharField(max_length=20, choices=[('clean','Clean'),('infected','Infected'),('error','Error'),('unknown','Unknown')], default='unknown')
    reason = models.TextField(blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    task_id = models.CharField(max_length=255, blank=True, help_text='Celery task id when scanned asynchronously')
    scanned_by = models.CharField(max_length=255, blank=True, help_text='Who/what triggered scan (e.g., worker id)')

    class Meta:
        ordering = ['-scanned_at']
        verbose_name = 'Template Scan Log'
        verbose_name_plural = 'Template Scan Logs'

    def __str__(self):
        return f"{self.template.name} - {self.result} at {self.scanned_at}"


class TemplateUsageLog(models.Model):
    """Track template usage for analytics"""
    
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.CASCADE,
        related_name='usage_logs'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='template_usage'
    )
    
    action = models.CharField(
        max_length=20,
        choices=[
            ('view', 'Viewed'),
            ('download', 'Downloaded'),
            ('generate', 'Generated Document'),
            ('customize', 'Customized'),
        ]
    )
    
    document_reference = models.CharField(max_length=100, blank=True, help_text="Invoice/Contract ID etc")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Template Usage Log"
        verbose_name_plural = "Template Usage Logs"
    
    def __str__(self):
        return f"{self.template.name} - {self.action} by {self.user}"
