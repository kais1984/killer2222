"""
Finance Accounting Views
"""

from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from decimal import Decimal
from financeaccounting.models import JournalEntry, Account, FinancialReport
from financeaccounting.forms import AccountForm, JournalEntryForm, StockMovementForm
from inventory.models import StockMovement


class AccountingDashboardView(LoginRequiredMixin, TemplateView):
    """Main accounting dashboard"""
    template_name = 'modules/accounting_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Summary statistics
        accounts = Account.objects.filter(is_active=True)
        total_accounts = accounts.count()
        
        journal_entries = JournalEntry.objects.all()
        total_entries = journal_entries.count()
        
        stock_movements = StockMovement.objects.all()
        total_movements = stock_movements.count()
        
        # Recent transactions
        recent_entries = journal_entries.order_by('-entry_date')[:5]
        recent_movements = stock_movements.order_by('-created_at')[:5]
        
        # Account balances
        assets_balance = Decimal('0.00')
        liabilities_balance = Decimal('0.00')
        equity_balance = Decimal('0.00')
        
        for account in accounts:
            balance = account.get_balance()
            if account.account_type == 'asset':
                assets_balance += balance
            elif account.account_type == 'liability':
                liabilities_balance += balance
            elif account.account_type == 'equity':
                equity_balance += balance
        
        context.update({
            'total_accounts': total_accounts,
            'total_entries': total_entries,
            'total_movements': total_movements,
            'recent_entries': recent_entries,
            'recent_movements': recent_movements,
            'assets_balance': assets_balance,
            'liabilities_balance': liabilities_balance,
            'equity_balance': equity_balance,
            'net_position': assets_balance - (liabilities_balance + equity_balance),
        })
        
        return context


class JournalEntryListView(LoginRequiredMixin, ListView):
    """Journal entry list view"""
    template_name = 'modules/journal_entry_list.html'
    model = JournalEntry
    paginate_by = 50
    context_object_name = 'journal_entries'
    
    def get_queryset(self):
        return JournalEntry.objects.all().order_by('-entry_date', '-created_at')


class AccountListView(LoginRequiredMixin, ListView):
    """Chart of accounts view"""
    template_name = 'modules/account_list.html'
    model = Account
    paginate_by = 50
    context_object_name = 'accounts'
    
    def get_queryset(self):
        return Account.objects.all().order_by('account_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate balances for all accounts
        accounts_with_balance = []
        for account in context['accounts']:
            accounts_with_balance.append({
                'account': account,
                'balance': account.get_balance()
            })
        context['accounts_with_balance'] = accounts_with_balance
        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    """Create new account"""
    template_name = 'modules/account_form.html'
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy('financeaccounting:account_list')


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    """Update account"""
    template_name = 'modules/account_form.html'
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy('financeaccounting:account_list')


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """Delete account"""
    template_name = 'modules/account_confirm_delete.html'
    model = Account
    success_url = reverse_lazy('financeaccounting:account_list')


class StockMovementListView(LoginRequiredMixin, ListView):
    """Stock movement audit trail view"""
    template_name = 'modules/stock_movement_list.html'
    model = StockMovement
    paginate_by = 50
    context_object_name = 'stock_movements'
    
    def get_queryset(self):
        return StockMovement.objects.all().order_by('-created_at')


class StockMovementCreateView(LoginRequiredMixin, CreateView):
    """Create stock movement"""
    template_name = 'modules/stock_movement_form.html'
    model = StockMovement
    form_class = StockMovementForm
    success_url = reverse_lazy('financeaccounting:stock_movement_list')
    
    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)


class FinancialReportListView(LoginRequiredMixin, ListView):
    """Financial reports view"""
    template_name = 'modules/financial_report_list.html'
    model = FinancialReport
    paginate_by = 50
    context_object_name = 'reports'
    
    def get_queryset(self):
        return FinancialReport.objects.all().order_by('-report_date')
