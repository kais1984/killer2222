from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from sales.models import Invoice
from inventory.models import Product
from rentals.models import RentalAgreement


class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    """Reports module dashboard"""
    template_name = 'modules/reports_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_sales'] = Invoice.objects.count()
        context['total_products'] = Product.objects.count()
        context['total_rentals'] = RentalAgreement.objects.count()
        return context


class SalesReportView(LoginRequiredMixin, TemplateView):
    """Sales report view"""
    template_name = 'modules/sales_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoices'] = Invoice.objects.all().order_by('-invoice_date')
        return context


class InventoryReportView(LoginRequiredMixin, TemplateView):
    """Inventory report view"""
    template_name = 'modules/inventory_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context
