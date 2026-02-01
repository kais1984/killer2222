"""
Reporting views for sales, GL, and data exports
"""

from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sales.models import Sale, Invoice
from financeaccounting.models import JournalEntry, Account
from inventory.models import Product
from crm.models import Client
from reports.pdf_services import InvoicePDFGenerator, SalesReportPDFGenerator, GLReportPDFGenerator
from reports.excel_services import ExcelExportService, ExcelImportService
import json


class ReportingDashboardView(LoginRequiredMixin, TemplateView):
    """Main reporting dashboard with quick shortcuts"""
    template_name = 'modules/reporting_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Today's metrics
        today = timezone.now().date()
        today_sales = Sale.objects.filter(sale_date__date=today)
        
        context['today_sales_count'] = today_sales.count()
        context['today_revenue'] = sum(s.total_amount for s in today_sales)
        context['today_items'] = sum(len(s.lines.all()) for s in today_sales)
        
        # This month metrics
        month_start = today.replace(day=1)
        month_sales = Sale.objects.filter(sale_date__date__gte=month_start)
        
        context['month_sales_count'] = month_sales.count()
        context['month_revenue'] = sum(s.total_amount for s in month_sales)
        
        # Year metrics
        year_start = today.replace(month=1, day=1)
        year_sales = Sale.objects.filter(sale_date__date__gte=year_start)
        
        context['year_sales_count'] = year_sales.count()
        context['year_revenue'] = sum(s.total_amount for s in year_sales)
        
        # Recent invoices
        context['recent_invoices'] = Invoice.objects.all().order_by('-invoice_date')[:5]
        
        # Pending payments (filter in Python since status is a property)
        all_invoices = Invoice.objects.all()
        pending_invoices = [inv for inv in all_invoices if inv.status in ['unpaid', 'partial']]
        context['pending_invoices_count'] = len(pending_invoices)
        context['pending_amount'] = sum(inv.sale.total_amount for inv in pending_invoices)
        
        return context


class SalesReportView(LoginRequiredMixin, TemplateView):
    """Generate and display sales reports"""
    template_name = 'modules/sales_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from query params
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        query = Sale.objects.all()
        
        if date_from:
            query = query.filter(sale_date__date__gte=date_from)
        if date_to:
            query = query.filter(sale_date__date__lte=date_to)
        
        sales = query.order_by('-sale_date')
        
        # Calculate metrics
        total_revenue = sum(s.total_amount for s in sales)
        total_items = sum(len(s.lines.all()) for s in sales)
        avg_transaction = total_revenue / len(sales) if sales.exists() else 0
        
        # Top customers
        top_customers = {}
        for sale in sales:
            customer_name = f"{sale.customer.first_name} {sale.customer.last_name}"
            if customer_name not in top_customers:
                top_customers[customer_name] = {'count': 0, 'total': 0}
            top_customers[customer_name]['count'] += 1
            top_customers[customer_name]['total'] += sale.total_amount
        
        context['sales'] = sales
        context['total_revenue'] = total_revenue
        context['total_items'] = total_items
        context['avg_transaction'] = avg_transaction
        context['total_sales'] = len(sales)
        context['top_customers'] = dict(sorted(top_customers.items(), 
                                               key=lambda x: x[1]['total'], 
                                               reverse=True)[:5])
        context['date_from'] = date_from
        context['date_to'] = date_to
        
        return context


class GLReportView(LoginRequiredMixin, TemplateView):
    """General Ledger reporting"""
    template_name = 'modules/gl_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        query = JournalEntry.objects.all()
        
        if date_from:
            query = query.filter(entry_date__date__gte=date_from)
        if date_to:
            query = query.filter(entry_date__date__lte=date_to)
        
        entries = query.order_by('-entry_date')
        
        # Calculate totals
        total_debits = 0
        total_credits = 0
        for entry in entries:
            for line in entry.lines.all():
                if line.line_type == 'debit':
                    total_debits += line.amount
                else:
                    total_credits += line.amount
        
        # Account balances
        accounts = Account.objects.all()
        account_balances = {}
        for account in accounts:
            balance = 0
            for entry in entries:
                for line in entry.lines.filter(account=account):
                    if line.line_type == 'debit':
                        balance += line.amount
                    else:
                        balance -= line.amount
            account_balances[account.account_name] = balance
        
        context['entries'] = entries[:100]  # Limit display
        context['total_debits'] = total_debits
        context['total_credits'] = total_credits
        context['is_balanced'] = abs(total_debits - total_credits) < 0.01
        context['account_balances'] = account_balances
        context['date_from'] = date_from
        context['date_to'] = date_to
        
        return context


class InventoryReportView(LoginRequiredMixin, TemplateView):
    """Inventory report"""
    template_name = 'modules/inventory_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        products = Product.objects.all()
        
        # Metrics
        total_products = products.count()
        low_stock = products.filter(quantity_in_stock__lt=10).count()
        total_inventory_value = sum(p.quantity_in_stock * p.cost_price for p in products)
        
        context['products'] = products.order_by('name')
        context['total_products'] = total_products
        context['low_stock'] = low_stock
        context['total_inventory_value'] = total_inventory_value
        
        return context


class InvoicePDFView(LoginRequiredMixin, View):
    """Generate invoice PDF"""
    
    def get(self, request, pk):
        try:
            invoice = Invoice.objects.get(pk=pk)
            generator = InvoicePDFGenerator(invoice)
            pdf_buffer = generator.generate()
            
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            return response
        except Invoice.DoesNotExist:
            return HttpResponse('Invoice not found', status=404)


class SalesReportPDFView(LoginRequiredMixin, View):
    """Generate sales report PDF"""
    
    def get(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        query = Sale.objects.all()
        
        if date_from:
            query = query.filter(sale_date__date__gte=date_from)
        if date_to:
            query = query.filter(sale_date__date__lte=date_to)
        
        sales = list(query.order_by('-sale_date'))
        
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None
        
        generator = SalesReportPDFGenerator(sales, date_from_obj, date_to_obj)
        pdf_buffer = generator.generate()
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        return response


class GLReportPDFView(LoginRequiredMixin, View):
    """Generate GL report PDF"""
    
    def get(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        query = JournalEntry.objects.all()
        
        if date_from:
            query = query.filter(entry_date__date__gte=date_from)
        if date_to:
            query = query.filter(entry_date__date__lte=date_to)
        
        entries = list(query.order_by('-entry_date'))
        
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None
        
        generator = GLReportPDFGenerator(entries, date_from_obj, date_to_obj)
        pdf_buffer = generator.generate()
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="gl_report.pdf"'
        return response


class SalesReportExcelView(LoginRequiredMixin, View):
    """Export sales report to Excel"""
    
    def get(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        query = Sale.objects.all()
        
        if date_from:
            query = query.filter(sale_date__date__gte=date_from)
        if date_to:
            query = query.filter(sale_date__date__lte=date_to)
        
        sales = list(query.order_by('-sale_date'))
        
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None
        
        excel_buffer = ExcelExportService.export_sales_report(sales, date_from_obj, date_to_obj)
        
        response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
        return response


class InvoicesExcelView(LoginRequiredMixin, View):
    """Export invoices to Excel"""
    
    def get(self, request):
        invoices = Invoice.objects.all().order_by('-invoice_date')
        excel_buffer = ExcelExportService.export_invoices(invoices)
        
        response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="invoices.xlsx"'
        return response


class InventoryExcelView(LoginRequiredMixin, View):
    """Export inventory to Excel"""
    
    def get(self, request):
        products = Product.objects.all()
        excel_buffer = ExcelExportService.export_inventory(products)
        
        response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="inventory.xlsx"'
        return response


class GLExcelView(LoginRequiredMixin, View):
    """Export GL to Excel"""
    
    def get(self, request):
        entries = JournalEntry.objects.all().order_by('-entry_date')
        excel_buffer = ExcelExportService.export_gl_report(entries)
        
        response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="gl_report.xlsx"'
        return response


class ProductImportView(LoginRequiredMixin, TemplateView):
    """Import products from Excel"""
    template_name = 'modules/product_import.html'
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No file uploaded'})
        
        file = request.FILES['file']
        
        # Save temp file
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.name)
        
        with open(temp_path, 'wb+') as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
        
        try:
            result = ExcelImportService.import_products(temp_path)
            os.remove(temp_path)
            
            return JsonResponse({
                'success': True,
                'message': f"Successfully imported {result['imported']} products",
                'imported': result['imported'],
                'errors': result['errors']
            })
        except Exception as e:
            os.remove(temp_path)
            return JsonResponse({'success': False, 'message': str(e)})


class CustomerImportView(LoginRequiredMixin, TemplateView):
    """Import customers from Excel"""
    template_name = 'modules/customer_import.html'
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No file uploaded'})
        
        file = request.FILES['file']
        
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.name)
        
        with open(temp_path, 'wb+') as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
        
        try:
            result = ExcelImportService.import_customers(temp_path)
            os.remove(temp_path)
            
            return JsonResponse({
                'success': True,
                'message': f"Successfully imported {result['imported']} customers",
                'imported': result['imported'],
                'errors': result['errors']
            })
        except Exception as e:
            os.remove(temp_path)
            return JsonResponse({'success': False, 'message': str(e)})
