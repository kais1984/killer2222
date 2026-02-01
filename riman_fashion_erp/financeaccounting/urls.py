"""
Finance Accounting URLs
"""

from django.urls import path
from financeaccounting.views import (
    AccountingDashboardView,
    JournalEntryListView,
    AccountListView,
    AccountCreateView,
    AccountUpdateView,
    AccountDeleteView,
    StockMovementListView,
    StockMovementCreateView,
    FinancialReportListView,
)

app_name = 'financeaccounting'

urlpatterns = [
    # Dashboard
    path('', AccountingDashboardView.as_view(), name='dashboard'),
    
    # Journal Entries
    path('journal-entries/', JournalEntryListView.as_view(), name='journal_entry_list'),
    
    # Chart of Accounts
    path('accounts/', AccountListView.as_view(), name='account_list'),
    path('accounts/add/', AccountCreateView.as_view(), name='account_create'),
    path('accounts/<uuid:pk>/edit/', AccountUpdateView.as_view(), name='account_edit'),
    path('accounts/<uuid:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),
    
    # Stock Movements
    path('stock-movements/', StockMovementListView.as_view(), name='stock_movement_list'),
    path('stock-movements/add/', StockMovementCreateView.as_view(), name='stock_movement_create'),
    
    # Financial Reports
    path('reports/', FinancialReportListView.as_view(), name='financial_report_list'),
]
