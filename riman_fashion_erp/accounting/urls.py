from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reports.services import DashboardMetricsService
from accounting.views import (
    ExpenseListView, ExpenseCreateView, ExpenseDetailView, ExpenseUpdateView,
    ExpenseSubmitView, ExpenseApprovalView, ExpensePostGLView, ExpensePostGLAjaxView
)


class DashboardMetricsView(APIView):
    """Get dashboard KPIs"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            metrics = DashboardMetricsService.get_kpis()
            return Response(metrics)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class FinancialReportView(APIView):
    """Get P&L report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.role in ['admin', 'accountant', 'manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        try:
            from reports.services import FinancialReportService
            from datetime import datetime
            
            year = int(request.query_params.get('year', datetime.now().year))
            month = int(request.query_params.get('month', datetime.now().month))
            
            pl_report = FinancialReportService.profit_and_loss(year, month)
            return Response(pl_report)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


# Phase 3: Expense Management URLs
urlpatterns = [
    path('dashboard-metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('financial-report/', FinancialReportView.as_view(), name='financial-report'),
    
    # Expense management routes (Phase 3)
    path('expenses/', ExpenseListView.as_view(), name='expense_list'),
    path('expenses/add/', ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/', ExpenseDetailView.as_view(), name='expense_detail'),
    path('expenses/<int:pk>/edit/', ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/<int:pk>/submit/', ExpenseSubmitView.as_view(), name='expense_submit'),
    path('expenses/<int:pk>/approve/', ExpenseApprovalView.as_view(), name='expense_approve'),
    path('expenses/<int:pk>/post-gl/', ExpensePostGLView.as_view(), name='expense_post_gl'),
    path('expenses/<int:pk>/post-gl-ajax/', ExpensePostGLAjaxView.as_view(), name='expense_post_gl_ajax'),
]
