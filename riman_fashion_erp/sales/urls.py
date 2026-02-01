from django.urls import path
from sales.views import (
    SalesDashboardView, SaleListView, SaleDetailView, SaleCreateView, 
    InvoiceListView, PromotionListView, PromotionCreateView,
    InvoiceDetailView, InvoiceCreateView, InvoiceUpdateView,
    InvoiceDepositCreateView, PaymentRecordView, InvoicePostToGLView
)

urlpatterns = [
    path('', SalesDashboardView.as_view(), name='sales_dashboard'),
    path('sales/', SaleListView.as_view(), name='sale_list'),
    path('sales/add/', SaleCreateView.as_view(), name='sale_add'),
    path('orders/add/', SaleCreateView.as_view(), name='order_add'),
    path('sales/<uuid:pk>/view/', SaleDetailView.as_view(), name='sale_detail'),
    
    # Invoice URLs
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/add/', InvoiceCreateView.as_view(), name='invoice_add'),
    path('invoices/<uuid:pk>/view/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<uuid:pk>/edit/', InvoiceUpdateView.as_view(), name='invoice_edit'),
    path('invoices/deposit/add/', InvoiceDepositCreateView.as_view(), name='invoice_deposit_add'),
    path('invoices/<uuid:pk>/post-gl/', InvoicePostToGLView.as_view(), name='invoice_post_gl'),
    
    # Payment URLs
    path('payments/add/', PaymentRecordView.as_view(), name='payment_add'),
    
    # Promotion URLs
    path('promotions/', PromotionListView.as_view(), name='promotion_list'),
    path('promotions/create/', PromotionCreateView.as_view(), name='promotion_create'),
]
