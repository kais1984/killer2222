"""
Core app views for dashboard and company settings
"""

from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import CompanySettings
from core.serializers import CompanySettingsSerializer
from core.forms import CompanySettingsForm


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view with KPIs"""
    template_name = 'dashboard.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            company = CompanySettings.objects.first()
            context['company'] = company
        except:
            pass
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'profile.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class CompanySettingsUpdateView(LoginRequiredMixin, UpdateView):
    """Update company settings including logo upload"""
    model = CompanySettings
    form_class = CompanySettingsForm
    template_name = 'company_settings.html'
    success_url = reverse_lazy('company_settings')
    login_url = '/admin/login/'
    
    def get_object(self):
        """Get or create company settings"""
        obj, created = CompanySettings.objects.get_or_create(pk=1)
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Company Settings'
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    """System settings view"""
    template_name = 'settings.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            company = CompanySettings.objects.first()
            context['company'] = company
        except:
            pass
        return context


class CompanySettingsView(APIView):
    """API endpoint for company settings management"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retrieve company settings"""
        try:
            settings = CompanySettings.objects.first()
            if not settings:
                settings = CompanySettings.objects.create()
            serializer = CompanySettingsSerializer(settings)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    def put(self, request):
        """Update company settings (admin only)"""
        if not request.user.role in ['admin', 'manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        try:
            settings = CompanySettings.objects.first()
            if not settings:
                settings = CompanySettings.objects.create()
            
            serializer = CompanySettingsSerializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class GlobalSearchView(LoginRequiredMixin, TemplateView):
    """Global search across all modules"""
    template_name = 'search_results.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        results = {
            'contracts': [],
            'clients': [],
            'products': [],
            'invoices': [],
            'stock_movements': [],
            'gl_accounts': [],
            'query': query
        }
        
        if query:
            # Search contracts
            from crm.models import Client, Appointment, ClientNote
            from inventory.models import Product, StockMovement
            from sales.models import Invoice, Sale, Promotion
            from accounting.models import ChartOfAccounts
            from django.db.models import Q
            
            results['clients'] = Client.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )[:10]
            
            results['products'] = Product.objects.filter(
                Q(name__icontains=query) |
                Q(sku__icontains=query)
            )[:10]
            
            results['invoices'] = Invoice.objects.filter(
                Q(invoice_number__icontains=query)
            )[:10]
            
            results['stock_movements'] = StockMovement.objects.filter(
                Q(movement_number__icontains=query) |
                Q(product__name__icontains=query)
            )[:10]
            
            results['gl_accounts'] = ChartOfAccounts.objects.filter(
                Q(account_code__icontains=query) |
                Q(account_name__icontains=query)
            )[:10]
            
            # Remove contracts from results dict since it's empty
            results.pop('contracts', None)
        
        context.update(results)
        return context


class SearchSuggestionsAPIView(LoginRequiredMixin, APIView):
    """API endpoint for search suggestions"""
    login_url = '/admin/login/'
    
    def get(self, request):
        from rest_framework.response import Response
        query = request.GET.get('q', '').strip()
        suggestions = []
        
        if not query or len(query) < 2:
            return Response([])
        
        from crm.models import Client
        from inventory.models import Product
        from sales.models import Invoice
        from django.db.models import Q
        
        # Get clients
        clients = Client.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )[:5]
        for client in clients:
            suggestions.append({
                'icon': 'users',
                'label': f'{client.first_name} {client.last_name}',
                'subtitle': client.email or client.phone,
                'value': f'{client.first_name} {client.last_name}',
                'type': 'client'
            })
        
        # Get products
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(sku__icontains=query)
        )[:5]
        for product in products:
            suggestions.append({
                'icon': 'box',
                'label': product.name,
                'subtitle': f'SKU: {product.sku}',
                'value': product.sku or product.name,
                'type': 'product'
            })
        
        # Get invoices
        invoices = Invoice.objects.filter(
            invoice_number__icontains=query
        )[:5]
        for invoice in invoices:
            suggestions.append({
                'icon': 'file-text',
                'label': f'Invoice {invoice.invoice_number}',
                'subtitle': f'Amount: ${invoice.total_amount}',
                'value': invoice.invoice_number,
                'type': 'invoice'
            })
        
        return Response(suggestions)
