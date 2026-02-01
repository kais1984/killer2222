from django.db import models
from django.core.validators import MinValueValidator
from crm.models import Client
from core.models import BaseModel


class SupportTicket(BaseModel):
    """Customer support ticket tracking"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    ]
    
    CATEGORY_CHOICES = [
        ('complaint', 'Complaint'),
        ('inquiry', 'Inquiry'),
        ('request', 'Request'),
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('other', 'Other'),
    ]
    
    ticket_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='support_tickets')
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    assigned_to = models.CharField(max_length=255, blank=True)  # Support agent
    
    resolution = models.TextField(blank=True)
    resolution_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['client', 'status']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"


class TicketComment(BaseModel):
    """Comments/replies on support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='comments')
    
    author = models.CharField(max_length=255)
    author_type = models.CharField(max_length=20, choices=[
        ('customer', 'Customer'),
        ('support', 'Support Staff'),
        ('internal', 'Internal'),
    ])
    
    content = models.TextField()
    is_internal = models.BooleanField(default=False)  # Not visible to customer
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment on {self.ticket.ticket_number}"


class TicketAttachment(models.Model):
    """Attachments to support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='attachments')
    
    file = models.FileField(upload_to='support/attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.CharField(max_length=255)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_date']
    
    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.filename}"


class KnowledgeBase(BaseModel):
    """Knowledge base articles"""
    article_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=100)
    
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords for search")
    
    is_published = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.article_number} - {self.title}"


class FAQ(BaseModel):
    """Frequently Asked Questions"""
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=100)
    
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.question[:50]


class Warranty(BaseModel):
    """Product warranty tracking"""
    WARRANTY_TYPE_CHOICES = [
        ('manufacturing', 'Manufacturing Warranty'),
        ('extended', 'Extended Warranty'),
        ('none', 'No Warranty'),
    ]
    
    warranty_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='warranties')
    
    product = models.CharField(max_length=255)  # Product details
    serial_number = models.CharField(max_length=100, blank=True)
    
    warranty_type = models.CharField(max_length=50, choices=WARRANTY_TYPE_CHOICES)
    warranty_start_date = models.DateField()
    warranty_end_date = models.DateField()
    
    terms_conditions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.warranty_number} - {self.product}"


class WarrantyClaim(BaseModel):
    """Warranty claim tracking"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_service', 'In Service'),
        ('completed', 'Completed'),
    ]
    
    claim_number = models.CharField(max_length=50, unique=True)
    warranty = models.ForeignKey(Warranty, on_delete=models.CASCADE, related_name='claims')
    
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    submission_date = models.DateField()
    resolution_date = models.DateField(null=True, blank=True)
    
    claim_decision = models.CharField(max_length=500, blank=True)
    compensation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.claim_number} - {self.warranty.product}"


class SurveyTemplate(BaseModel):
    """Customer satisfaction survey templates"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class SurveyQuestion(models.Model):
    """Survey questions"""
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text'),
        ('rating', 'Rating (1-5)'),
        ('multiple_choice', 'Multiple Choice'),
        ('yes_no', 'Yes/No'),
    ]
    
    survey = models.ForeignKey(SurveyTemplate, on_delete=models.CASCADE, related_name='questions')
    
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPE_CHOICES)
    options = models.CharField(max_length=1000, blank=True, help_text="Comma-separated options for multiple choice")
    
    sequence = models.IntegerField()
    is_required = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['sequence']
    
    def __str__(self):
        return f"{self.survey.name} - Q{self.sequence}"


class SurveyResponse(BaseModel):
    """Customer survey responses"""
    survey = models.ForeignKey(SurveyTemplate, on_delete=models.CASCADE, related_name='responses')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.survey.name} - {self.client.name if self.client else 'Anonymous'}"


class SurveyAnswer(models.Model):
    """Individual survey answers"""
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    
    answer_text = models.TextField()
    
    class Meta:
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"Answer to {self.question.question_text}"
