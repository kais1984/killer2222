"""
Admin configuration for all models
"""

from django.contrib import admin
from core.models import CompanySettings, User
from suppliers.models import Supplier, PurchaseInvoice, PurchaseInvoiceItem, SupplierPayment
from inventory.models import Category, Collection, Product, ProductImage, Warehouse, StockLocation, StockMovement, LowStockAlert
from sales.models import Order, OrderItem, Invoice, InvoiceItem, Payment, Promotion, CustomOrder
from rentals.models import RentalAgreement, RentalItem, RentalReturn, RentalPayment, RentalInventory
from crm.models import Client, Measurement, Appointment, ClientNote, ClientPreference, ClientInteraction
from accounting.models import ChartOfAccounts, JournalEntry, JournalEntryLine, Income, Expense, Asset, Liability, FinancialPeriod

# Core Admin
@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'phone', 'currency_code']
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'company_slug', 'logo', 'brand_color', 'accent_color')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Financial Settings', {
            'fields': ('currency_symbol', 'currency_code', 'tax_type', 'tax_rate')
        }),
        ('Invoice Settings', {
            'fields': ('invoice_prefix', 'invoice_next_number', 'invoice_footer')
        }),
        ('System Settings', {
            'fields': ('financial_year_start', 'low_stock_threshold')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# Supplier Admin
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'phone', 'email', 'status', 'rating']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['name', 'email', 'phone']

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'total_amount', 'amount_paid', 'status']
    list_filter = ['status', 'invoice_date', 'supplier']
    search_fields = ['invoice_number']

@admin.register(PurchaseInvoiceItem)
class PurchaseInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'product', 'quantity', 'unit_price', 'line_total']

# Inventory Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'season', 'year', 'launch_date']
    list_filter = ['season', 'year']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'dress_type', 'size', 'color', 'sale_price', 'quantity_in_stock']
    list_filter = ['dress_type', 'size', 'color', 'is_active']
    search_fields = ['sku', 'name']

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location_type', 'current_stock', 'capacity']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'created_at']
    list_filter = ['movement_type', 'created_at']

# Sales Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'client', 'order_date', 'status']
    list_filter = ['status', 'order_date']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'total_amount', 'payment_status', 'status']
    list_filter = ['status', 'payment_status', 'invoice_date']

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'discount_type', 'discount_value', 'status']
    list_filter = ['status', 'start_date']

@admin.register(CustomOrder)
class CustomOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'client', 'status', 'expected_completion_date']
    list_filter = ['status']

# Rental Admin
@admin.register(RentalAgreement)
class RentalAgreementAdmin(admin.ModelAdmin):
    list_display = ['rental_number', 'client', 'rental_date', 'return_date', 'status']
    list_filter = ['status', 'rental_date']

@admin.register(RentalInventory)
class RentalInventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'total_available', 'currently_rented', 'in_maintenance']

# CRM Admin
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'client_type', 'total_purchases']
    list_filter = ['client_type', 'status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client', 'appointment_type', 'scheduled_date', 'scheduled_time', 'status']
    list_filter = ['appointment_type', 'status', 'scheduled_date']

@admin.register(ClientPreference)
class ClientPreferenceAdmin(admin.ModelAdmin):
    list_display = ['client', 'preferred_styles']

# Accounting Admin
@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(admin.ModelAdmin):
    list_display = ['account_code', 'account_name', 'account_type', 'current_balance']
    list_filter = ['account_type', 'is_active']

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'entry_date', 'total_debit', 'total_credit', 'status']
    list_filter = ['status', 'entry_date']

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['income_date', 'income_type', 'description', 'amount']
    list_filter = ['income_type', 'income_date']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['expense_date', 'expense_type', 'description', 'amount']
    list_filter = ['expense_type', 'expense_date']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_name', 'asset_type', 'acquisition_cost', 'current_value']
    list_filter = ['asset_type', 'is_active']

@admin.register(FinancialPeriod)
class FinancialPeriodAdmin(admin.ModelAdmin):
    list_display = ['period_name', 'period_start', 'period_end', 'status', 'net_profit_loss']
    list_filter = ['status', 'period_start']
