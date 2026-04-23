from django.contrib import admin
from django.utils.html import format_html
from sales.models import Sale, SaleLine, Invoice, Payment, Promotion


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Admin for Sales"""
    list_display = ['sale_number', 'customer', 'total_amount', 'payment_status', 'created_at']
    list_filter = ['created_at']
    search_fields = ['sale_number', 'customer__first_name', 'customer__last_name']
    readonly_fields = ['sale_number', 'total_amount', 'payment_status', 'created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ['sale_number', 'customer', 'created_by', 'created_at']
        }),
        ('Totals', {
            'fields': ['subtotal', 'tax_amount', 'total_amount']
        }),
        ('Status', {
            'fields': ['payment_status', 'notes']
        }),
    )


@admin.register(SaleLine)
class SaleLineAdmin(admin.ModelAdmin):
    """Admin for Sale line items"""
    list_display = ['sale', 'product', 'quantity', 'unit_price', 'line_total']
    list_filter = ['sale__created_at', 'product__category']
    search_fields = ['sale__sale_number', 'product__sku']
    readonly_fields = ['line_total']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for Invoices"""
    list_display = ['invoice_number', 'sale_or_contract', 'invoice_type', 'total_amount', 'status_badge', 'invoice_date']
    list_filter = ['invoice_type', 'is_posted', 'invoice_date']
    search_fields = ['invoice_number', 'sale__sale_number', 'contract__contract_number']
    readonly_fields = ['invoice_number', 'is_posted', 'posted_at', 'amount_paid', 'amount_due', 'status']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ['invoice_number', 'invoice_type', 'invoice_date', 'due_date']
        }),
        ('Source', {
            'fields': ['sale', 'contract']
        }),
        ('Amounts', {
            'fields': ['subtotal', 'tax_amount', 'total_amount', 'amount_paid', 'amount_due', 'status']
        }),
        ('GL Posting', {
            'fields': ['is_posted', 'posted_at', 'posted_by', 'gl_posted'],
            'classes': ['collapse']
        }),
        ('Audit', {
            'fields': ['created_by', 'created_at'],
            'classes': ['collapse']
        }),
    )
    
    def sale_or_contract(self, obj):
        return obj.sale or obj.contract
    sale_or_contract.short_description = 'Source'
    
    def status_badge(self, obj):
        colors = {
            'unpaid': 'red',
            'partial': 'orange',
            'paid': 'green'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payments"""
    list_display = ['payment_number', 'sale_customer', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['payment_number', 'sale__sale_number', 'reference']
    readonly_fields = ['payment_number', 'recorded_at', 'created_by']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ['payment_number', 'sale', 'amount']
        }),
        ('Payment Details', {
            'fields': ['payment_method', 'payment_date', 'reference']
        }),
        ('Audit', {
            'fields': ['created_by', 'recorded_at'],
            'classes': ['collapse']
        }),
    )
    
    def sale_customer(self, obj):
        return obj.sale.customer.name if obj.sale else '-'
    sale_customer.short_description = 'Customer'


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Admin for Promotions"""
    list_display = ['name', 'code', 'discount_display', 'status', 'created_at']
    list_filter = ['status', 'discount_type', 'created_at']
    search_fields = ['name', 'code', 'description']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ['name', 'code', 'description']
        }),
        ('Discount', {
            'fields': ['discount_type', 'discount_value']
        }),
        ('Dates & Usage', {
            'fields': ['start_date', 'end_date', 'max_uses']
        }),
        ('Status', {
            'fields': ['status']
        }),
    )
    
    def discount_display(self, obj):
        suffix = '%' if obj.discount_type == 'percentage' else f'{obj.sale.customer.outstanding_balance.currency}'
        return f"{obj.discount_value}{suffix}"
    discount_display.short_description = 'Discount'
