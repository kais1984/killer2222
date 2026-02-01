from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from crm.models import Client, ClientInteraction, Contract
from crm.forms import ClientForm, ClientInteractionForm, ContractForm
from inventory.models import RentalReservation


class CRMDashboardView(LoginRequiredMixin, TemplateView):
    """CRM module dashboard"""
    template_name = 'modules/crm_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all()[:10]
        context['contacts'] = ClientInteraction.objects.all()[:10]
        context['contracts'] = Contract.objects.filter(status__in=['draft', 'approved'])[:10]
        context['total_clients'] = Client.objects.count()
        context['active_contracts'] = Contract.objects.filter(status__in=['approved', 'in_production', 'ready']).count()
        return context


class ClientListView(LoginRequiredMixin, ListView):
    """Client list view"""
    template_name = 'modules/client_list.html'
    model = Client
    paginate_by = 20
    context_object_name = 'clients'
    
    def get_queryset(self):
        return Client.objects.all().order_by('-created_at')


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Create new client"""
    model = Client
    form_class = ClientForm
    template_name = 'modules/client_form.html'
    success_url = reverse_lazy('client_list')


class ClientInteractionListView(LoginRequiredMixin, ListView):
    """Client interaction list view"""
    template_name = 'modules/contact_list.html'
    model = ClientInteraction
    paginate_by = 20
    context_object_name = 'contacts'
    
    def get_queryset(self):
        return ClientInteraction.objects.all()


class ClientInteractionCreateView(LoginRequiredMixin, CreateView):
    """Create new client interaction"""
    model = ClientInteraction
    form_class = ClientInteractionForm
    template_name = 'modules/contact_form.html'
    success_url = reverse_lazy('contact_list')


# ============ CONTRACT VIEWS (PHASE 1) ============

class ContractListView(LoginRequiredMixin, ListView):
    """List all contracts"""
    model = Contract
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Contract.objects.all().order_by('-contract_date')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by type
        contract_type = self.request.GET.get('type')
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        
        # Search by contract number or client name
        search = self.request.GET.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(contract_number__icontains=search) |
                Q(client__first_name__icontains=search) |
                Q(client__last_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_statuses'] = Contract.STATUS_CHOICES
        context['contract_types'] = Contract.CONTRACT_TYPE_CHOICES
        return context


class ContractDetailView(LoginRequiredMixin, DetailView):
    """View contract details"""
    model = Contract
    template_name = 'contracts/contract_detail.html'
    context_object_name = 'contract'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract = self.get_object()
        
        # Get related invoices
        from sales.models import Invoice
        context['invoices'] = Invoice.objects.filter(contract=contract)
        
        # Get rental reservations
        context['reservations'] = RentalReservation.objects.filter(contract=contract)
        
        # Show remaining balance
        context['remaining_balance'] = contract.get_remaining_balance()
        
        return context


class ContractCreateView(LoginRequiredMixin, CreateView):
    """Create new contract"""
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('contract_detail', kwargs={'pk': self.object.pk})


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    """Edit contract (only if not invoiced)"""
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    
    def get(self, request, *args, **kwargs):
        contract = self.get_object()
        if not contract.can_edit():
            messages.error(request, 'This contract cannot be edited because invoicing has started.')
            return redirect('contract_detail', pk=contract.pk)
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        contract = self.get_object()
        if not contract.can_edit():
            messages.error(request, 'This contract cannot be edited because invoicing has started.')
            return redirect('contract_detail', pk=contract.pk)
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('contract_detail', kwargs={'pk': self.object.pk})


class ContractApproveView(LoginRequiredMixin, UpdateView):
    """Approve contract"""
    model = Contract
    fields = []
    
    def post(self, request, *args, **kwargs):
        contract = self.get_object()
        
        if not contract.can_approve():
            messages.error(request, f'Cannot approve contract in {contract.get_status_display()} status.')
            return redirect('contract_detail', pk=contract.pk)
        
        contract.status = 'approved'
        contract.approved_at = timezone.now()
        contract.approved_by = request.user
        contract.save()
        
        messages.success(request, f'Contract {contract.contract_number} approved.')
        return redirect('contract_detail', pk=contract.pk)


class ContractProductionView(LoginRequiredMixin, UpdateView):
    """Mark contract as in production"""
    model = Contract
    fields = []
    
    def post(self, request, *args, **kwargs):
        contract = self.get_object()
        
        if contract.contract_type not in ['custom_sale', 'custom_rent']:
            messages.error(request, 'Only custom contracts can move to production.')
            return redirect('contract_detail', pk=contract.pk)
        
        if contract.status not in ['approved']:
            messages.error(request, 'Contract must be approved before starting production.')
            return redirect('contract_detail', pk=contract.pk)
        
        contract.status = 'in_production'
        contract.production_start_date = timezone.now().date()
        contract.save()
        
        messages.success(request, f'Contract {contract.contract_number} marked as in production.')
        return redirect('contract_detail', pk=contract.pk)


class ContractReadyView(LoginRequiredMixin, UpdateView):
    """Mark contract as ready"""
    model = Contract
    fields = []
    
    def post(self, request, *args, **kwargs):
        contract = self.get_object()
        
        if contract.status not in ['approved', 'in_production']:
            messages.error(request, 'Contract must be approved or in production.')
            return redirect('contract_detail', pk=contract.pk)
        
        contract.status = 'ready'
        contract.save()
        
        messages.success(request, f'Contract {contract.contract_number} marked as ready.')
        return redirect('contract_detail', pk=contract.pk)


class ContractCompleteView(LoginRequiredMixin, UpdateView):
    """Mark contract as completed"""
    model = Contract
    fields = []
    
    def post(self, request, *args, **kwargs):
        contract = self.get_object()
        
        if contract.status != 'ready':
            messages.error(request, 'Contract must be ready before completion.')
            return redirect('contract_detail', pk=contract.pk)
        
        contract.status = 'completed'
        contract.save()
        
        messages.success(request, f'Contract {contract.contract_number} completed.')
        return redirect('contract_detail', pk=contract.pk)
