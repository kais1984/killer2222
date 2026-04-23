"""
RIMAN FASHION ERP - URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from rest_framework import routers
from core.views import DashboardView, CompanySettingsView, ProfileView, SettingsView, CompanySettingsUpdateView, GlobalSearchView, SearchSuggestionsAPIView
from documents.views import (
    ContractListView, DownloadContractView, ViewContractView,
    TemplateLibraryView, TemplateDetailView, TemplatePreviewView,
    TemplateDownloadView, InvoiceTemplateListView, ContractTemplateListView,
    UploadTemplateView, DownloadTemplateFileView, ReinstateTemplateView
)
from sales.views import SalesDashboardView, InvoiceListView, InvoiceCreateView, SaleListView, SaleDetailView, SaleCreateView, PromotionListView, PromotionCreateView
from inventory.views import InventoryDashboardView, ProductListView, StockListView, WarehouseListView, ProductCreateView, StockCreateView, WarehouseCreateView, ProductDetailView, ProductUpdateView, ProductImageUploadView
from crm.views import CRMDashboardView, ClientListView, ClientInteractionListView, ClientCreateView, ClientInteractionCreateView
from rentals.views import RentalsDashboardView, RentalListView, RentalCreateView
from suppliers.views import SuppliersDashboardView, SupplierListView, PurchaseOrderListView, SupplierCreateView, PurchaseOrderCreateView
from reports.views import ReportsDashboardView, SalesReportView, InventoryReportView
from financeaccounting.views import AccountingDashboardView

# Initialize API router
router = routers.DefaultRouter()

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include([
        path('auth/', include('core.urls_auth')),
        path('search/suggestions/', SearchSuggestionsAPIView.as_view(), name='search_suggestions_api'),
        path('suppliers/', include('suppliers.urls')),
        path('inventory/', include('inventory.urls')),
        path('sales/', include('sales.urls')),
        path('rentals/', include('rentals.urls')),
        path('crm/', include('crm.urls')),
        path('reports/', include('reports.urls')),
    ])),
    
    # Web Views - Main
    path('', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('company-settings/', CompanySettingsUpdateView.as_view(), name='company_settings'),
    path('api/company-settings/', CompanySettingsView.as_view(), name='company_settings_api'),
    path('logout/', LogoutView.as_view(next_page='dashboard'), name='logout'),
    path('search/', GlobalSearchView.as_view(), name='global_search'),
    
    # Web Views - Contracts
    path('contracts/', ContractListView.as_view(), name='contracts_list'),
    path('contracts/<str:contract_id>/view/', ViewContractView.as_view(), name='view_contract'),
    path('contracts/<str:contract_id>/download/', DownloadContractView.as_view(), name='download_contract'),
    
    # Web Views - Templates
    path('templates/', TemplateLibraryView.as_view(), name='template_library'),
    path('templates/upload/', UploadTemplateView.as_view(), name='upload_template'),
    path('templates/invoices/', InvoiceTemplateListView.as_view(), name='invoice_templates'),
    path('templates/contracts/', ContractTemplateListView.as_view(), name='contract_templates'),
    path('templates/<slug:slug>/', TemplateDetailView.as_view(), name='template_detail'),
    path('templates/<slug:slug>/preview/', TemplatePreviewView.as_view(), name='template_preview'),
    path('templates/<slug:slug>/download/', TemplateDownloadView.as_view(), name='template_download'),
    path('templates/<slug:slug>/download-file/', DownloadTemplateFileView.as_view(), name='download_template_file'),
    path('templates/<slug:slug>/reinstate/', ReinstateTemplateView.as_view(), name='template_reinstate'),
    
    # Web Views - Sales
    path('sales/', SalesDashboardView.as_view(), name='sales_dashboard'),
    path('sales/sales/', SaleListView.as_view(), name='sale_list'),
    path('sales/sales/add/', SaleCreateView.as_view(), name='sale_add'),
    path('sales/orders/add/', SaleCreateView.as_view(), name='order_add'),
    path('sales/sales/<uuid:pk>/view/', SaleDetailView.as_view(), name='sale_detail'),
    path('sales/invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('sales/invoices/add/', InvoiceCreateView.as_view(), name='invoice_add'),
    path('sales/promotions/', PromotionListView.as_view(), name='promotion_list'),
    path('sales/promotions/add/', PromotionCreateView.as_view(), name='promotion_add'),
    
    # Web Views - Inventory
    path('inventory/', InventoryDashboardView.as_view(), name='inventory_dashboard'),
    path('inventory/products/', ProductListView.as_view(), name='product_list'),
    path('inventory/products/add/', ProductCreateView.as_view(), name='product_add'),
    path('inventory/products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('inventory/products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('inventory/products/<int:product_id>/upload-image/', ProductImageUploadView.as_view(), name='product_upload_image'),
    path('inventory/stock/', StockListView.as_view(), name='stock_list'),
    path('inventory/stock/add/', StockCreateView.as_view(), name='stock_add'),
    path('inventory/warehouses/', WarehouseListView.as_view(), name='warehouse_list'),
    path('inventory/warehouses/add/', WarehouseCreateView.as_view(), name='warehouse_add'),
    
    # Web Views - CRM
    path('crm/', CRMDashboardView.as_view(), name='crm_dashboard'),
    path('crm/clients/', ClientListView.as_view(), name='client_list'),
    path('crm/clients/add/', ClientCreateView.as_view(), name='client_add'),
    path('crm/contacts/', ClientInteractionListView.as_view(), name='contact_list'),
    path('crm/contacts/add/', ClientInteractionCreateView.as_view(), name='contact_add'),
    
    # Web Views - Rentals
    path('rentals/', RentalsDashboardView.as_view(), name='rentals_dashboard'),
    path('rentals/list/', RentalListView.as_view(), name='rental_list'),
    path('rentals/add/', RentalCreateView.as_view(), name='rental_add'),
    
    # Web Views - Suppliers
    path('suppliers/', SuppliersDashboardView.as_view(), name='suppliers_dashboard'),
    path('suppliers/list/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', SupplierCreateView.as_view(), name='supplier_add'),
    path('suppliers/orders/', PurchaseOrderListView.as_view(), name='purchase_order_list'),
    path('suppliers/orders/add/', PurchaseOrderCreateView.as_view(), name='purchase_order_add'),
    
    # Web Views - Reports & Exports
    path('reports/', include('reports.urls')),
    
    # Web Views - Finance Accounting
    path('accounting/', include('financeaccounting.urls')),
    
    # Web Views - HR (Human Resources)
    path('hr/', include('hr.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
