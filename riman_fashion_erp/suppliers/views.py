from django.views.generic import TemplateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from suppliers.models import Supplier, PurchaseInvoice
from suppliers.forms import SupplierForm, PurchaseInvoiceForm


class SuppliersDashboardView(LoginRequiredMixin, TemplateView):
    """Suppliers module dashboard"""
    template_name = 'modules/suppliers_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = Supplier.objects.all()[:10]
        context['orders'] = PurchaseInvoice.objects.all()[:10]
        return context


class SupplierListView(LoginRequiredMixin, ListView):
    """Supplier list view"""
    template_name = 'modules/supplier_list.html'
    model = Supplier
    paginate_by = 20
    context_object_name = 'suppliers'
    
    def get_queryset(self):
        return Supplier.objects.all().order_by('-created_at')


class SupplierCreateView(LoginRequiredMixin, CreateView):
    """Create new supplier"""
    model = Supplier
    form_class = SupplierForm
    template_name = 'modules/supplier_form.html'
    success_url = reverse_lazy('supplier_list')


class PurchaseOrderListView(LoginRequiredMixin, ListView):
    """Purchase order list view"""
    template_name = 'modules/purchase_order_list.html'
    model = PurchaseInvoice
    paginate_by = 20
    context_object_name = 'orders'
    
    def get_queryset(self):
        return PurchaseInvoice.objects.all().order_by('-created_at')


class PurchaseOrderCreateView(LoginRequiredMixin, CreateView):
    """Create new purchase order"""
    model = PurchaseInvoice
    form_class = PurchaseInvoiceForm
    template_name = 'modules/purchase_order_form.html'
    success_url = reverse_lazy('purchase_order_list')
