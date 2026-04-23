from django.db import models
from core.models import BaseModel


class ReportTemplate(BaseModel):
    """Custom report templates"""
    REPORT_TYPE_CHOICES = [
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('financial', 'Financial Report'),
        ('production', 'Production Report'),
        ('quality', 'Quality Report'),
        ('customer', 'Customer Report'),
        ('supplier', 'Supplier Report'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    sql_query = models.TextField(blank=True, help_text="Custom SQL query for report")
    
    include_fields = models.TextField(help_text="Comma-separated field names to include")
    grouping = models.CharField(max_length=255, blank=True)
    filtering = models.TextField(blank=True, help_text="JSON filter conditions")
    
    is_public = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class DashboardWidget(BaseModel):
    """Dashboard widgets for executive dashboard"""
    WIDGET_TYPE_CHOICES = [
        ('kpi', 'KPI Card'),
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('gauge', 'Gauge'),
        ('trend', 'Trend'),
    ]
    
    name = models.CharField(max_length=255)
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    
    metric_name = models.CharField(max_length=255)
    metric_value = models.CharField(max_length=255, blank=True)
    metric_unit = models.CharField(max_length=50, blank=True)
    
    data_source = models.CharField(max_length=255)  # Model/query source
    refresh_interval = models.IntegerField(default=300, help_text="Seconds")
    
    widget_order = models.IntegerField(default=0)
    column_span = models.IntegerField(default=1, help_text="Grid column span")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['widget_order']
    
    def __str__(self):
        return self.title


class SalesAnalytics(BaseModel):
    """Sales analytics and trends"""
    period_date = models.DateField(unique=True)
    
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_quantity = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    total_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    pending_orders = models.IntegerField(default=0)
    
    top_product = models.CharField(max_length=255, blank=True)
    top_customer = models.CharField(max_length=255, blank=True)
    
    growth_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-period_date']
    
    def __str__(self):
        return f"Sales - {self.period_date}"


class InventoryAnalytics(BaseModel):
    """Inventory analytics and metrics"""
    period_date = models.DateField(unique=True)
    
    total_items = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    fast_moving = models.IntegerField(default=0)
    slow_moving = models.IntegerField(default=0)
    non_moving = models.IntegerField(default=0)
    
    average_turnover = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stock_out_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-period_date']
    
    def __str__(self):
        return f"Inventory - {self.period_date}"


class ProfitabilityAnalytics(BaseModel):
    """Product and customer profitability analysis"""
    period_date = models.DateField(unique=True)
    
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    most_profitable_product = models.CharField(max_length=255, blank=True)
    most_profitable_customer = models.CharField(max_length=255, blank=True)
    
    roi = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-period_date']
    
    def __str__(self):
        return f"Profitability - {self.period_date}"


class CustomerAnalytics(BaseModel):
    """Customer behavior and metrics"""
    period_date = models.DateField(unique=True)
    
    total_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    inactive_customers = models.IntegerField(default=0)
    
    customer_lifetime_value_avg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customer_acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    churn_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-period_date']
    
    def __str__(self):
        return f"Customer - {self.period_date}"


class AuditLog(BaseModel):
    """System audit and activity log"""
    user = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    
    module = models.CharField(max_length=100)
    record_id = models.CharField(max_length=100, blank=True)
    
    before_value = models.TextField(blank=True)
    after_value = models.TextField(blank=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['module', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action}"
