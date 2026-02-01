"""
Human Resources Management Models: Employees, Payroll, Attendance, Performance
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Department(models.Model):
    """Company departments"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Position(models.Model):
    """Job positions"""
    
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.department}"
    
    class Meta:
        unique_together = ['title', 'department']
        ordering = ['department', 'title']


class Employee(models.Model):
    """Employee information"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='employees')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    date_joined = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    photo = models.ImageField(upload_to='employees/%Y/', null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Attendance(models.Model):
    """Employee attendance tracking"""
    
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('leave', 'Leave'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"


class Payroll(models.Model):
    """Employee payroll records"""
    
    PAYROLL_PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('bi_weekly', 'Bi-weekly'),
        ('weekly', 'Weekly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_records')
    period_start = models.DateField()
    period_end = models.DateField()
    period_type = models.CharField(max_length=20, choices=PAYROLL_PERIOD_CHOICES, default='monthly')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    notes = models.TextField(blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period_end']
        verbose_name_plural = 'Payroll Records'
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.period_start} to {self.period_end}"
    
    def calculate_net(self):
        return self.base_salary + self.bonus - self.deductions


class Performance(models.Model):
    """Employee performance reviews"""
    
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews_given')
    review_date = models.DateField(auto_now_add=True)
    period = models.CharField(max_length=20)  # e.g., "Q1 2026"
    overall_rating = models.IntegerField(choices=RATING_CHOICES)
    productivity = models.IntegerField(choices=RATING_CHOICES)
    quality = models.IntegerField(choices=RATING_CHOICES)
    teamwork = models.IntegerField(choices=RATING_CHOICES)
    attendance = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-review_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.period}"
    
    @property
    def average_rating(self):
        ratings = [self.productivity, self.quality, self.teamwork, self.attendance]
        return round(sum(ratings) / len(ratings), 1)


class Leave(models.Model):
    """Employee leave requests"""
    
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
        ('maternity', 'Maternity Leave'),
        ('unpaid', 'Unpaid Leave'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='leaves_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type} ({self.start_date})"
    
    @property
    def days_requested(self):
        return (self.end_date - self.start_date).days + 1
