from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel


class BudgetYear(BaseModel):
    """Financial year/period for budgeting"""
    fiscal_year = models.IntegerField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ], default='draft')
    
    class Meta:
        ordering = ['-fiscal_year']
    
    def __str__(self):
        return f"FY {self.fiscal_year}"


class BudgetCategory(models.Model):
    """Budget categories"""
    CODE_CHOICES = [
        ('revenue', 'Revenue'),
        ('cogs', 'Cost of Goods Sold'),
        ('operations', 'Operating Expenses'),
        ('marketing', 'Marketing & Sales'),
        ('personnel', 'Personnel'),
        ('equipment', 'Equipment'),
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('other', 'Other'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    category_type = models.CharField(max_length=50, choices=CODE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Budget(BaseModel):
    """Budget planning and allocation"""
    year = models.ForeignKey(BudgetYear, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name='budgets')
    
    period = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ])
    
    jan = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    feb = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mar = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    apr = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    may = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    jun = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    jul = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    aug = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sep = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    oct = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nov = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    dec = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['year', 'category', 'period']
        ordering = ['category']
    
    def __str__(self):
        return f"{self.year} - {self.category.name}"
    
    @property
    def total_budget(self):
        return sum([self.jan, self.feb, self.mar, self.apr, self.may, self.jun,
                    self.jul, self.aug, self.sep, self.oct, self.nov, self.dec])


class FixedAsset(BaseModel):
    """Fixed asset register"""
    ASSET_TYPE_CHOICES = [
        ('machinery', 'Machinery'),
        ('equipment', 'Equipment'),
        ('building', 'Building'),
        ('vehicle', 'Vehicle'),
        ('furniture', 'Furniture'),
        ('computer', 'Computer'),
        ('other', 'Other'),
    ]
    
    asset_number = models.CharField(max_length=50, unique=True)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    acquisition_date = models.DateField()
    acquisition_cost = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    
    useful_life_years = models.IntegerField(validators=[MinValueValidator(1)])
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    location = models.CharField(max_length=255, blank=True)
    supplier = models.CharField(max_length=255, blank=True)
    
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('disposed', 'Disposed'),
    ], default='active')
    
    class Meta:
        ordering = ['-acquisition_date']
    
    def __str__(self):
        return f"{self.asset_number} - {self.name}"
    
    @property
    def book_value(self):
        from datetime import date
        months_owned = (date.today() - self.acquisition_date).days / 30.44
        months_life = self.useful_life_years * 12
        if months_owned > months_life:
            return self.salvage_value
        depreciation_amount = (self.acquisition_cost - self.salvage_value) * (months_owned / months_life)
        return self.acquisition_cost - depreciation_amount


class Depreciation(BaseModel):
    """Depreciation tracking"""
    DEPRECIATION_METHOD_CHOICES = [
        ('straight_line', 'Straight Line'),
        ('declining_balance', 'Declining Balance'),
        ('units_of_production', 'Units of Production'),
    ]
    
    asset = models.ForeignKey(FixedAsset, on_delete=models.CASCADE, related_name='depreciation_records')
    
    depreciation_method = models.CharField(max_length=50, choices=DEPRECIATION_METHOD_CHOICES, default='straight_line')
    
    fiscal_year = models.IntegerField()
    month = models.IntegerField()
    
    monthly_depreciation = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    accumulated_depreciation = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['asset', 'fiscal_year', 'month']
        ordering = ['-fiscal_year', '-month']
    
    def __str__(self):
        return f"{self.asset.asset_number} - {self.fiscal_year}/{self.month:02d}"


class CashFlowProjection(BaseModel):
    """Cash flow forecasting"""
    fiscal_year = models.IntegerField()
    category = models.CharField(max_length=100)  # e.g., "Operating Activities", "Investing Activities"
    
    jan = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    feb = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mar = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    apr = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    may = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    jun = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    jul = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    aug = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sep = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    oct = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nov = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    dec = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['fiscal_year', 'category']
        ordering = ['-fiscal_year', 'category']
    
    def __str__(self):
        return f"{self.fiscal_year} - {self.category}"


class PayrollEmployee(BaseModel):
    """Employee payroll information"""
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
    ]
    
    employee_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    
    bank_account = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class PayrollDeduction(models.Model):
    """Payroll deduction types"""
    DEDUCTION_TYPE_CHOICES = [
        ('income_tax', 'Income Tax'),
        ('social_security', 'Social Security'),
        ('health_insurance', 'Health Insurance'),
        ('retirement', 'Retirement'),
        ('loan', 'Loan Repayment'),
        ('other', 'Other'),
    ]
    
    employee = models.ForeignKey(PayrollEmployee, on_delete=models.CASCADE, related_name='deductions')
    
    deduction_type = models.CharField(max_length=50, choices=DEDUCTION_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ['employee', 'deduction_type']
    
    def __str__(self):
        return f"{self.employee.name} - {self.deduction_type}"


class Payroll(BaseModel):
    """Payroll records"""
    payroll_number = models.CharField(max_length=50, unique=True)
    fiscal_year = models.IntegerField()
    month = models.IntegerField()
    
    total_employees = models.IntegerField(validators=[MinValueValidator(0)])
    total_gross_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_net_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    employer_contribution = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_payroll_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
    ], default='draft')
    
    processed_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['fiscal_year', 'month']
        ordering = ['-fiscal_year', '-month']
    
    def __str__(self):
        return f"{self.payroll_number} - {self.fiscal_year}/{self.month:02d}"


class PayrollDetail(models.Model):
    """Individual employee payroll detail"""
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='details')
    employee = models.ForeignKey(PayrollEmployee, on_delete=models.CASCADE)
    
    days_worked = models.IntegerField(validators=[MinValueValidator(0)])
    hours_worked = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    overtime_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['payroll', 'employee']
    
    def __str__(self):
        return f"{self.payroll.payroll_number} - {self.employee.name}"


class TaxConfiguration(BaseModel):
    """Tax setup and configuration"""
    TAX_TYPE_CHOICES = [
        ('income_tax', 'Income Tax'),
        ('vat', 'VAT/GST'),
        ('sales_tax', 'Sales Tax'),
        ('payroll_tax', 'Payroll Tax'),
    ]
    
    tax_type = models.CharField(max_length=50, choices=TAX_TYPE_CHOICES)
    tax_name = models.CharField(max_length=100)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    
    applicable_from = models.DateField()
    applicable_to = models.DateField(null=True, blank=True)
    
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-applicable_from']
    
    def __str__(self):
        return f"{self.tax_type} - {self.tax_rate}%"
