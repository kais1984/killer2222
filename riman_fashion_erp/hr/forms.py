"""HR app forms for employee management, payroll, attendance"""

from django import forms
from django.forms import inlineformset_factory
from .models import Employee, Department, Position, Attendance, Payroll, Performance, Leave


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Department description'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['title', 'department', 'description', 'salary_min', 'salary_max']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job title'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone', 'department', 
                  'position', 'gender', 'date_of_birth', 'date_joined', 'status', 'salary', 
                  'photo', 'address', 'city', 'country']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., EMP-001'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status', 'check_in', 'check_out', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'check_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['employee', 'period_start', 'period_end', 'period_type', 'base_salary', 
                  'bonus', 'deductions', 'net_salary', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_type': forms.Select(attrs={'class': 'form-control'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'net_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PerformanceForm(forms.ModelForm):
    class Meta:
        model = Performance
        fields = ['employee', 'reviewer', 'period', 'overall_rating', 'productivity', 
                  'quality', 'teamwork', 'attendance', 'comments', 'goals']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'reviewer': forms.Select(attrs={'class': 'form-control'}),
            'period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Q1 2026'}),
            'overall_rating': forms.Select(attrs={'class': 'form-control'}),
            'productivity': forms.Select(attrs={'class': 'form-control'}),
            'quality': forms.Select(attrs={'class': 'form-control'}),
            'teamwork': forms.Select(attrs={'class': 'form-control'}),
            'attendance': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason', 'status']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
