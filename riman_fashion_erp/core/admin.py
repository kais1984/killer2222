from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import User, CompanySettings, AuditLog, Notification

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Permissions', {'fields': ('role',)}),
        ('Additional Info', {'fields': ('phone', 'profile_image')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']

@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'company_slug', 'logo')
        }),
        ('Branding', {
            'fields': ('brand_color', 'accent_color')
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
        ('Document Upload Settings', {
            'fields': ('upload_max_size', 'allowed_extensions', 'enforce_mime', 'use_s3', 'virus_scan'),
            'description': 'Configure document upload limits, allowed file types, and scanning/storage options.'
        }),
    )

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'description']
    readonly_fields = ['timestamp', 'user', 'action', 'model_name', 'object_id']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'priority', 'is_read', 'created_at']
    list_filter = ['priority', 'is_read', 'created_at']
    search_fields = ['title', 'message']
