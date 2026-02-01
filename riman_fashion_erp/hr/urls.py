"""HR app URL configuration"""

from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Dashboard
    path('', views.hr_dashboard, name='dashboard'),
    
    # Employees
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/<uuid:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/add/', views.EmployeeCreateView.as_view(), name='employee_add'),
    path('employees/<uuid:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    path('employees/<uuid:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_add'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    
    # Attendance
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/add/', views.AttendanceCreateView.as_view(), name='attendance_add'),
    path('attendance/<uuid:pk>/edit/', views.AttendanceUpdateView.as_view(), name='attendance_edit'),
    
    # Payroll
    path('payroll/', views.PayrollListView.as_view(), name='payroll_list'),
    path('payroll/add/', views.PayrollCreateView.as_view(), name='payroll_add'),
    path('payroll/<uuid:pk>/edit/', views.PayrollUpdateView.as_view(), name='payroll_edit'),
    
    # Performance
    path('performance/', views.PerformanceListView.as_view(), name='performance_list'),
    path('performance/add/', views.PerformanceCreateView.as_view(), name='performance_add'),
    path('performance/<uuid:pk>/edit/', views.PerformanceUpdateView.as_view(), name='performance_edit'),
    
    # Leave
    path('leave/', views.LeaveListView.as_view(), name='leave_list'),
    path('leave/add/', views.LeaveCreateView.as_view(), name='leave_add'),
    path('leave/<uuid:pk>/edit/', views.LeaveUpdateView.as_view(), name='leave_edit'),
    path('leave/<uuid:pk>/approve/', views.approve_leave, name='leave_approve'),
    path('leave/<uuid:pk>/reject/', views.reject_leave, name='leave_reject'),
]
