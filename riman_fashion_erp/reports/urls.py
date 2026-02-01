from django.urls import path
from reports.reporting_views import (
    ReportingDashboardView, SalesReportView, GLReportView, InventoryReportView,
    InvoicePDFView, SalesReportPDFView, GLReportPDFView,
    SalesReportExcelView, InvoicesExcelView, InventoryExcelView, GLExcelView,
    ProductImportView, CustomerImportView
)

urlpatterns = [
    # Dashboard
    path('', ReportingDashboardView.as_view(), name='reporting_dashboard'),
    
    # HTML Reports
    path('sales/', SalesReportView.as_view(), name='sales_report'),
    path('gl/', GLReportView.as_view(), name='gl_report'),
    path('inventory/', InventoryReportView.as_view(), name='inventory_report'),
    
    # PDF Exports
    path('invoice/<uuid:pk>/pdf/', InvoicePDFView.as_view(), name='invoice_pdf'),
    path('sales/pdf/', SalesReportPDFView.as_view(), name='sales_report_pdf'),
    path('gl/pdf/', GLReportPDFView.as_view(), name='gl_report_pdf'),
    
    # Excel Exports
    path('sales/excel/', SalesReportExcelView.as_view(), name='sales_report_excel'),
    path('invoices/excel/', InvoicesExcelView.as_view(), name='invoices_excel'),
    path('inventory/excel/', InventoryExcelView.as_view(), name='inventory_excel'),
    path('gl/excel/', GLExcelView.as_view(), name='gl_excel'),
    
    # Excel Imports
    path('products/import/', ProductImportView.as_view(), name='product_import'),
    path('customers/import/', CustomerImportView.as_view(), name='customer_import'),
]
