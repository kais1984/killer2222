"""HR app views for managing employees, payroll, attendance, performance"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Employee, Department, Position, Attendance, Payroll, Performance, Leave
from .forms import (EmployeeForm, DepartmentForm, PositionForm, AttendanceForm, 
                    PayrollForm, PerformanceForm, LeaveForm)


# ============ DASHBOARD ============
def hr_dashboard(request):
    """HR Dashboard overview"""
    context = {
        'total_employees': Employee.objects.filter(status='active').count(),
        'total_departments': Department.objects.count(),
        'pending_leaves': Leave.objects.filter(status='pending').count(),
        'recent_employees': Employee.objects.filter(status='active').order_by('-created_at')[:5],
    }
    return render(request, 'hr/dashboard.html', context)


# ============ EMPLOYEE MANAGEMENT ============
class EmployeeListView(LoginRequiredMixin, ListView):
    """List all employees"""
    model = Employee
    template_name = 'hr/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Employee.objects.select_related('department', 'position')
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(employee_id__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """Employee detail view"""
    model = Employee
    template_name = 'hr/employee_detail.html'
    context_object_name = 'employee'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        context['attendance_records'] = employee.attendance_records.all()[:10]
        context['payroll_records'] = employee.payroll_records.all()[:5]
        context['performance_reviews'] = employee.performance_reviews.all()[:3]
        return context


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    """Create new employee"""
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    """Update employee information"""
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    """Delete employee (marks as inactive)"""
    model = Employee
    template_name = 'hr/employee_confirm_delete.html'
    success_url = reverse_lazy('hr:employee_list')
    
    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        employee.status = 'terminated'
        employee.save()
        return redirect(self.success_url)


# ============ DEPARTMENT MANAGEMENT ============
class DepartmentListView(LoginRequiredMixin, ListView):
    """List all departments"""
    model = Department
    template_name = 'hr/department_list.html'
    context_object_name = 'departments'


class DepartmentCreateView(LoginRequiredMixin, CreateView):
    """Create new department"""
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')


class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    """Update department"""
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')


# ============ ATTENDANCE TRACKING ============
class AttendanceListView(LoginRequiredMixin, ListView):
    """List all attendance records"""
    model = Attendance
    template_name = 'hr/attendance_list.html'
    context_object_name = 'attendance_records'
    paginate_by = 50
    
    def get_queryset(self):
        return Attendance.objects.select_related('employee').order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_filter'] = self.request.GET.get('employee', '')
        return context


class AttendanceCreateView(LoginRequiredMixin, CreateView):
    """Record attendance"""
    model = Attendance
    form_class = AttendanceForm
    template_name = 'hr/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')


class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
    """Update attendance record"""
    model = Attendance
    form_class = AttendanceForm
    template_name = 'hr/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')


# ============ PAYROLL MANAGEMENT ============
class PayrollListView(LoginRequiredMixin, ListView):
    """List all payroll records"""
    model = Payroll
    template_name = 'hr/payroll_list.html'
    context_object_name = 'payroll_records'
    paginate_by = 20
    
    def get_queryset(self):
        return Payroll.objects.select_related('employee').order_by('-period_end')


class PayrollCreateView(LoginRequiredMixin, CreateView):
    """Create payroll record"""
    model = Payroll
    form_class = PayrollForm
    template_name = 'hr/payroll_form.html'
    success_url = reverse_lazy('hr:payroll_list')


class PayrollUpdateView(LoginRequiredMixin, UpdateView):
    """Update payroll record"""
    model = Payroll
    form_class = PayrollForm
    template_name = 'hr/payroll_form.html'
    success_url = reverse_lazy('hr:payroll_list')


# ============ PERFORMANCE REVIEWS ============
class PerformanceListView(LoginRequiredMixin, ListView):
    """List all performance reviews"""
    model = Performance
    template_name = 'hr/performance_list.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def get_queryset(self):
        return Performance.objects.select_related('employee', 'reviewer').order_by('-review_date')


class PerformanceCreateView(LoginRequiredMixin, CreateView):
    """Create performance review"""
    model = Performance
    form_class = PerformanceForm
    template_name = 'hr/performance_form.html'
    success_url = reverse_lazy('hr:performance_list')


class PerformanceUpdateView(LoginRequiredMixin, UpdateView):
    """Update performance review"""
    model = Performance
    form_class = PerformanceForm
    template_name = 'hr/performance_form.html'
    success_url = reverse_lazy('hr:performance_list')


# ============ LEAVE MANAGEMENT ============
class LeaveListView(LoginRequiredMixin, ListView):
    """List all leave requests"""
    model = Leave
    template_name = 'hr/leave_list.html'
    context_object_name = 'leaves'
    paginate_by = 20
    
    def get_queryset(self):
        return Leave.objects.select_related('employee').order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_leaves'] = Leave.objects.filter(status='pending').count()
        return context


class LeaveCreateView(LoginRequiredMixin, CreateView):
    """Create leave request"""
    model = Leave
    form_class = LeaveForm
    template_name = 'hr/leave_form.html'
    success_url = reverse_lazy('hr:leave_list')


class LeaveUpdateView(LoginRequiredMixin, UpdateView):
    """Update leave request"""
    model = Leave
    form_class = LeaveForm
    template_name = 'hr/leave_form.html'
    success_url = reverse_lazy('hr:leave_list')


def approve_leave(request, pk):
    """Approve leave request"""
    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'approved'
    leave.approved_by = request.user
    from django.utils import timezone
    leave.approved_date = timezone.now()
    leave.save()
    return redirect('hr:leave_list')


def reject_leave(request, pk):
    """Reject leave request"""
    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'rejected'
    leave.save()
    return redirect('hr:leave_list')
