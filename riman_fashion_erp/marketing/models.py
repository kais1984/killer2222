from django.db import models
from django.core.validators import MinValueValidator
from crm.models import Client
from core.models import BaseModel


class EmailCampaign(BaseModel):
    """Email marketing campaign management"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]
    
    campaign_name = models.CharField(max_length=255, unique=True)
    campaign_code = models.CharField(max_length=50, unique=True)
    
    subject = models.CharField(max_length=255)
    preview_text = models.CharField(max_length=255, blank=True)
    
    content = models.TextField()
    html_content = models.TextField(blank=True)
    
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=255)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    scheduled_send_date = models.DateTimeField(null=True, blank=True)
    actual_send_date = models.DateTimeField(null=True, blank=True)
    
    recipients_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    open_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)
    
    unsubscribe_count = models.IntegerField(default=0)
    bounce_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.campaign_code} - {self.campaign_name}"
    
    @property
    def open_rate(self):
        if self.sent_count > 0:
            return (self.open_count / self.sent_count) * 100
        return 0
    
    @property
    def click_rate(self):
        if self.open_count > 0:
            return (self.click_count / self.open_count) * 100
        return 0


class SMSCampaign(BaseModel):
    """SMS marketing campaign"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]
    
    campaign_name = models.CharField(max_length=255, unique=True)
    campaign_code = models.CharField(max_length=50, unique=True)
    
    message = models.CharField(max_length=160)
    
    sender_id = models.CharField(max_length=20)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    scheduled_send_date = models.DateTimeField(null=True, blank=True)
    actual_send_date = models.DateTimeField(null=True, blank=True)
    
    recipients_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.campaign_code} - {self.campaign_name}"


class CustomerSegment(BaseModel):
    """Customer segmentation for targeted marketing"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    SEGMENTATION_TYPE_CHOICES = [
        ('demographic', 'Demographic'),
        ('behavioral', 'Behavioral'),
        ('geographic', 'Geographic'),
        ('value', 'Customer Value'),
        ('custom', 'Custom'),
    ]
    
    segmentation_type = models.CharField(max_length=50, choices=SEGMENTATION_TYPE_CHOICES)
    
    criteria = models.TextField(help_text="Segment criteria in JSON format")
    
    customer_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class SegmentMember(models.Model):
    """Customers in a segment"""
    segment = models.ForeignKey(CustomerSegment, on_delete=models.CASCADE, related_name='members')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['segment', 'client']
    
    def __str__(self):
        return f"{self.segment.name} - {self.client.name}"


class LoyaltyProgram(BaseModel):
    """Customer loyalty rewards program"""
    program_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    POINT_TYPE_CHOICES = [
        ('purchase', 'Purchase Points'),
        ('referral', 'Referral Points'),
        ('review', 'Review Points'),
        ('engagement', 'Engagement Points'),
    ]
    
    is_active = models.BooleanField(default=True)
    
    points_per_currency = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    points_expiry_days = models.IntegerField(null=True, blank=True, help_text="Days until points expire")
    
    minimum_points_redemption = models.IntegerField(default=100)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.program_name


class LoyaltyMember(BaseModel):
    """Customer loyalty program membership"""
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='members')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='loyalty_memberships')
    
    member_id = models.CharField(max_length=50, unique=True)
    
    tier = models.CharField(max_length=50, choices=[
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ], default='bronze')
    
    total_points = models.IntegerField(default=0)
    available_points = models.IntegerField(default=0)
    
    join_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['program', 'client']
    
    def __str__(self):
        return f"{self.member_id} - {self.client.name}"


class LoyaltyTransaction(BaseModel):
    """Points earn/redeem transactions"""
    TRANSACTION_TYPE_CHOICES = [
        ('earn', 'Points Earned'),
        ('redeem', 'Points Redeemed'),
        ('adjustment', 'Adjustment'),
        ('expiry', 'Points Expired'),
    ]
    
    loyalty_member = models.ForeignKey(LoyaltyMember, on_delete=models.CASCADE, related_name='transactions')
    
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    points = models.IntegerField()
    
    reference = models.CharField(max_length=100, blank=True)  # Order/Invoice reference
    description = models.TextField(blank=True)
    
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.loyalty_member.member_id} - {self.transaction_type}"


class RedemptionReward(BaseModel):
    """Rewards available for loyalty points redemption"""
    reward_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    REWARD_TYPE_CHOICES = [
        ('discount', 'Discount'),
        ('free_product', 'Free Product'),
        ('cashback', 'Cashback'),
        ('voucher', 'Voucher'),
        ('gift', 'Gift'),
    ]
    
    reward_type = models.CharField(max_length=50, choices=REWARD_TYPE_CHOICES)
    
    points_required = models.IntegerField(validators=[MinValueValidator(1)])
    reward_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    quantity_available = models.IntegerField(validators=[MinValueValidator(0)])
    quantity_redeemed = models.IntegerField(default=0)
    
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reward_name} - {self.points_required} points"
