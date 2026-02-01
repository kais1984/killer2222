from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html
from accounting.models import JournalEntry, ChartOfAccounts, Expense
from accounting.forms import AccountForm, JournalEntryForm, ExpenseForm, ExpenseSubmitForm, ExpenseApprovalForm


class AccountingDashboardView(LoginRequiredMixin, TemplateView):
    """Accounting module dashboard"""
    template_name = 'modules/accounting_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = ChartOfAccounts.objects.all()[:10]
        context['entries'] = JournalEntry.objects.all()[:10]
        return context


class AccountListView(LoginRequiredMixin, ListView):
    """Account list view"""
    template_name = 'modules/account_list.html'
    model = ChartOfAccounts
    paginate_by = 20
    context_object_name = 'accounts'
    
    def get_queryset(self):
        return ChartOfAccounts.objects.all()


class AccountCreateView(LoginRequiredMixin, CreateView):
    """Create new account"""
    model = ChartOfAccounts
    form_class = AccountForm
    template_name = 'modules/account_form.html'
    success_url = reverse_lazy('account_list')


class JournalEntryListView(LoginRequiredMixin, ListView):
    """Journal entry list view"""
    template_name = 'modules/journal_entry_list.html'
    model = JournalEntry
    paginate_by = 20
    context_object_name = 'entries'
    
    def get_queryset(self):
        return JournalEntry.objects.all().order_by('-entry_date')


class JournalEntryCreateView(LoginRequiredMixin, CreateView):
    """Create new journal entry"""
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'modules/journal_entry_form.html'
    success_url = reverse_lazy('journal_entry_list')


# Phase 3: Expense Management Views

class ExpenseListView(LoginRequiredMixin, ListView):
    """List all expenses (Phase 3)"""
    template_name = 'accounting/expense_list.html'
    model = Expense
    paginate_by = 20
    context_object_name = 'expenses'
    
    def get_queryset(self):
        return Expense.objects.all().order_by('-expense_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_expenses'] = Expense.objects.filter(status='posted').count()
        context['pending_approval'] = Expense.objects.filter(status='submitted').count()
        context['draft_count'] = Expense.objects.filter(status='draft').count()
        return context


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    """Create new expense (Phase 3)"""
    template_name = 'accounting/expense_form.html'
    model = Expense
    form_class = ExpenseForm
    
    def form_valid(self, form):
        expense = form.save(commit=False)
        expense.created_by = self.request.user
        expense.save()
        messages.success(self.request, f"Expense {expense.expense_number} created successfully")
        return redirect('expense_detail', pk=expense.pk)


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    """View expense details (Phase 3)"""
    template_name = 'accounting/expense_detail.html'
    model = Expense
    context_object_name = 'expense'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expense = self.get_object()
        context['can_edit'] = expense.can_edit()
        context['can_delete'] = expense.can_delete()
        context['can_approve'] = expense.can_approve()
        context['can_reject'] = expense.can_reject()
        return context


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    """Update expense (Phase 3)"""
    template_name = 'accounting/expense_form.html'
    model = Expense
    form_class = ExpenseForm
    
    def get_form(self, form_class=None):
        """Disable form if expense is posted"""
        form = super().get_form(form_class)
        if self.object.is_posted:
            for field in form.fields:
                form.fields[field].widget.attrs['disabled'] = True
        return form
    
    def form_valid(self, form):
        if not self.object.can_edit():
            messages.error(self.request, "Cannot edit expense in current status")
            return redirect('expense_detail', pk=self.object.pk)
        
        expense = form.save()
        messages.success(self.request, f"Expense {expense.expense_number} updated successfully")
        return redirect('expense_detail', pk=expense.pk)


class ExpenseSubmitView(LoginRequiredMixin, UpdateView):
    """Submit expense for approval (Phase 3)"""
    template_name = 'accounting/expense_submit.html'
    model = Expense
    form_class = ExpenseSubmitForm
    
    def get(self, request, *args, **kwargs):
        expense = self.get_object()
        if expense.status != 'draft':
            messages.error(request, "Only draft expenses can be submitted")
            return redirect('expense_detail', pk=expense.pk)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        expense = self.get_object()
        
        if not expense.can_edit():
            messages.error(self.request, "Cannot submit expense in current status")
            return redirect('expense_detail', pk=expense.pk)
        
        expense.status = 'submitted'
        expense.submitted_at = timezone.now()
        expense.submitted_by = self.request.user
        if form.cleaned_data.get('notes'):
            expense.notes = form.cleaned_data['notes']
        expense.save()
        
        messages.success(self.request, f"Expense {expense.expense_number} submitted for approval")
        return redirect('expense_detail', pk=expense.pk)


class ExpenseApprovalView(LoginRequiredMixin, UpdateView):
    """Approve/reject expense (Phase 3)"""
    template_name = 'accounting/expense_approval.html'
    model = Expense
    form_class = ExpenseApprovalForm
    
    def get(self, request, *args, **kwargs):
        expense = self.get_object()
        if not expense.can_approve():
            messages.error(request, "Expense is not pending approval")
            return redirect('expense_detail', pk=expense.pk)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        expense = self.get_object()
        decision = form.cleaned_data.get('decision')
        notes = form.cleaned_data.get('notes')
        
        if not expense.can_approve():
            messages.error(self.request, "Expense is not pending approval")
            return redirect('expense_detail', pk=expense.pk)
        
        if decision == 'approve':
            expense.status = 'approved'
            expense.approved_at = timezone.now()
            expense.approved_by = self.request.user
            if notes:
                expense.notes += f"\n\n[APPROVAL] {self.request.user}: {notes}"
            expense.save()
            messages.success(self.request, f"Expense {expense.expense_number} approved")
        else:
            expense.status = 'rejected'
            if notes:
                expense.notes += f"\n\n[REJECTION] {self.request.user}: {notes}"
            expense.save()
            messages.warning(self.request, f"Expense {expense.expense_number} rejected")
        
        return redirect('expense_detail', pk=expense.pk)


class ExpensePostGLView(LoginRequiredMixin, UpdateView):
    """Post expense to GL (Phase 3)"""
    template_name = 'accounting/expense_post_gl.html'
    model = Expense
    fields = []
    
    def get(self, request, *args, **kwargs):
        expense = self.get_object()
        if expense.status != 'approved':
            messages.error(request, "Only approved expenses can be posted")
            return redirect('expense_detail', pk=expense.pk)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        expense = self.get_object()
        
        if expense.status != 'approved':
            messages.error(self.request, "Only approved expenses can be posted to GL")
            return redirect('expense_detail', pk=expense.pk)
        
        try:
            expense.post_to_gl(self.request.user)
            messages.success(self.request, f"Expense {expense.expense_number} posted to GL successfully")
        except ValueError as e:
            messages.error(self.request, f"Failed to post expense: {str(e)}")
        
        return redirect('expense_detail', pk=expense.pk)


class ExpensePostGLAjaxView(LoginRequiredMixin, DetailView):
    """AJAX endpoint to post expense to GL (Phase 3)"""
    model = Expense
    
    def post(self, request, *args, **kwargs):
        expense = self.get_object()
        
        if expense.status != 'approved':
            return JsonResponse({'success': False, 'error': 'Expense must be approved first'}, status=400)
        
        try:
            expense.post_to_gl(request.user)
            return JsonResponse({
                'success': True,
                'message': f"Expense {expense.expense_number} posted to GL",
                'status': expense.status
            })
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
