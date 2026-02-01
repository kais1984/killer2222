from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from sales.models import Invoice, Sale, Promotion, Payment
from sales.forms import PromotionForm, SaleForm, InvoiceForm, InvoiceDepositForm, PaymentForm


class SalesDashboardView(LoginRequiredMixin, TemplateView):
    """Sales module dashboard"""
    template_name = 'modules/sales_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoices'] = Invoice.objects.all().order_by('-invoice_date')[:10]
        context['sales'] = Sale.objects.all().order_by('-sale_date')[:10]
        return context


class SaleCreateView(LoginRequiredMixin, CreateView):
    """Create new sale view"""
    template_name = 'modules/sale_form.html'
    model = Sale
    form_class = SaleForm
    success_url = reverse_lazy('sale_list')
    login_url = '/admin/login/'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class InvoiceListView(LoginRequiredMixin, ListView):
    """Invoice list view"""
    template_name = 'modules/invoice_list.html'
    model = Invoice
    paginate_by = 20
    context_object_name = 'invoices'
    
    def get_queryset(self):
        return Invoice.objects.all().order_by('-invoice_date')


class SaleListView(LoginRequiredMixin, ListView):
    """Sale list view"""
    template_name = 'modules/sale_list.html'
    model = Sale
    paginate_by = 20
    context_object_name = 'sales'
    
    def get_queryset(self):
        return Sale.objects.all().order_by('-sale_date')


class SaleDetailView(LoginRequiredMixin, DetailView):
    """Sale detail view"""
    template_name = 'modules/sale_detail.html'
    model = Sale
    context_object_name = 'sale'
    pk_url_kwarg = 'pk'


class PromotionListView(LoginRequiredMixin, ListView):
    """Promotion list view"""
    template_name = 'modules/promotion_list.html'
    model = Promotion
    paginate_by = 20
    context_object_name = 'promotions'
    
    def get_queryset(self):
        return Promotion.objects.all().order_by('-created_at')


class PromotionCreateView(LoginRequiredMixin, CreateView):
    """Create promotion view"""
    template_name = 'modules/promotion_form.html'
    model = Promotion
    form_class = PromotionForm
    success_url = reverse_lazy('promotion_list')
    login_url = '/admin/login/'


# ===== INVOICE VIEWS =====

class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """Invoice detail view with payment tracking"""
    template_name = 'modules/invoice_detail.html'
    model = Invoice
    context_object_name = 'invoice'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()
        context['payments'] = invoice.payment_set.filter(reversed_at__isnull=True)
        context['remaining_balance'] = invoice.amount_due
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    """Create invoice from sale or contract"""
    template_name = 'modules/invoice_form.html'
    model = Invoice
    form_class = InvoiceForm
    success_url = reverse_lazy('invoice_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        
        # Validate contract invoicing rules
        if form.instance.contract:
            contract = form.instance.contract
            
            # Must be approved
            if not contract.can_invoice():
                raise ValidationError(f"Contract status '{contract.status}' cannot be invoiced")
            
            # Check for duplicate invoice types
            if form.instance.invoice_type in ['deposit', 'final']:
                existing = Invoice.objects.filter(
                    contract=contract,
                    invoice_type=form.instance.invoice_type
                ).exists()
                
                if existing:
                    form.add_error(None, f"{form.instance.get_invoice_type_display()} already exists for this contract")
                    return self.form_invalid(form)
            
            # Lock contract for invoicing
            contract.lock_for_invoicing()
        
        return super().form_valid(form)


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    """Update invoice (only if not posted)"""
    template_name = 'modules/invoice_form.html'
    model = Invoice
    form_class = InvoiceForm
    success_url = reverse_lazy('invoice_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        invoice = self.get_object()
        
        # Disable if posted
        if invoice.is_posted:
            for field in form.fields:
                form.fields[field].disabled = True
        
        return form


class InvoiceDepositCreateView(LoginRequiredMixin, CreateView):
    """Create deposit invoice for contract"""
    template_name = 'modules/invoice_deposit_form.html'
    model = Invoice
    form_class = InvoiceDepositForm
    success_url = reverse_lazy('invoice_list')
    
    def form_valid(self, form):
        form.instance.invoice_type = 'deposit'
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class PaymentRecordView(LoginRequiredMixin, CreateView):
    """Record payment against sale"""
    template_name = 'modules/payment_form.html'
    model = Payment
    form_class = PaymentForm
    success_url = reverse_lazy('invoice_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        
        # Validate amount not exceeding sale balance
        sale = form.instance.sale
        if form.instance.amount > sale.amount_due:
            form.add_error('amount', f"Payment exceeds outstanding balance of {sale.amount_due}")
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        
        return response


class InvoicePostToGLView(LoginRequiredMixin, DetailView):
    """Post invoice to GL for revenue recognition"""
    model = Invoice
    
    def post(self, request, *args, **kwargs):
        invoice = self.get_object()
        
        try:
            invoice.post_to_gl()
            return JsonResponse({'success': True, 'message': 'Invoice posted to GL'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
