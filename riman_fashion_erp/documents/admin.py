"""
Document Template Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import DocumentTemplate, InvoiceTemplate, ContractTemplate, TemplateUsageLog, TemplateScanLog


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type_badge', 'is_active_badge', 'is_default_badge', 'scan_status', 'version', 'created_at']
    list_filter = ['template_type', 'is_active', 'is_default', 'scan_status', 'created_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['id', 'version', 'created_at', 'updated_at', 'created_by', 'scan_status', 'quarantine_reason']
    
    fieldsets = (
        ('Identity', {
            'fields': ('id', 'name', 'slug', 'template_type')
        }),
        ('Content', {
            'fields': ('description', 'content', 'preview_image'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_default', 'scan_status', 'quarantine_reason')
        }),
        ('Version Control', {
            'fields': ('version', 'parent_template'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_active', 'make_inactive', 'set_as_default']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} templates activated.')
    make_active.short_description = 'Mark selected as active'

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} templates deactivated.')
    make_inactive.short_description = 'Mark selected as inactive'

    def set_as_default(self, request, queryset):
        for template in queryset:
            template.set_as_default()
        self.message_user(request, f'Set as defaults.')
    set_as_default.short_description = 'Set as default template'

    def reinstate_templates(self, request, queryset):
        updated = queryset.update(is_active=True, scan_status='unknown', quarantine_reason='')
        self.message_user(request, f'{updated} templates reinstated.')
    reinstate_templates.short_description = 'Reinstate selected quarantined templates'

    def template_type_badge(self, obj):
        colors = {
            'invoice': '#17a2b8',
            'contract': '#dc3545',
            'receipt': '#28a745',
            'purchase_order': '#007bff',
            'delivery_note': '#6f42c1',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.template_type, '#6c757d'),
            obj.get_template_type_display()
        )
    template_type_badge.short_description = 'Type'
    
    def is_active_badge(self, obj):
        color = '#28a745' if obj.is_active else '#6c757d'
        text = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color, text
        )
    is_active_badge.short_description = 'Status'
    
    def is_default_badge(self, obj):
        if obj.is_default:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 5px 10px; border-radius: 3px;">Default</span>'
            )
        return '-'
    is_default_badge.short_description = 'Default'
    
    actions = ['make_active', 'make_inactive', 'set_as_default', 'reinstate_templates']
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} templates activated.')
    make_active.short_description = 'Mark selected as active'
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} templates deactivated.')
    make_inactive.short_description = 'Mark selected as inactive'
    
    def set_as_default(self, request, queryset):
        for template in queryset:
            template.set_as_default()
        self.message_user(request, f'Set as defaults.')
    set_as_default.short_description = 'Set as default template'


@admin.register(InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ['template', 'invoice_prefix', 'color_scheme', 'show_tax', 'show_discount']
    list_filter = ['color_scheme', 'show_tax', 'show_discount', 'created_at']
    search_fields = ['template__name', 'invoice_prefix']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Template Link', {
            'fields': ('template',)
        }),
        ('Invoice Configuration', {
            'fields': ('invoice_prefix', 'invoice_number_format')
        }),
        ('Display Options', {
            'fields': ('show_po_number', 'show_tax', 'show_discount', 'show_notes', 'show_terms')
        }),
        ('Styling', {
            'fields': ('company_logo_position', 'color_scheme', 'font_family')
        }),
        ('Default Text', {
            'fields': ('payment_terms_text',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ['template', 'contract_type', 'clauses_count']
    list_filter = ['contract_type', 'includes_payment_terms', 'includes_liability', 'created_at']
    search_fields = ['template__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Template Link', {
            'fields': ('template',)
        }),
        ('Contract Type', {
            'fields': ('contract_type',)
        }),
        ('Clauses', {
            'fields': (
                'includes_payment_terms',
                'includes_liability',
                'includes_confidentiality',
                'includes_termination',
                'includes_dispute_resolution'
            )
        }),
        ('Required Fields', {
            'fields': (
                'company_name_required',
                'client_name_required',
                'date_fields_required',
                'amount_fields_required'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def clauses_count(self, obj):
        count = sum([
            obj.includes_payment_terms,
            obj.includes_liability,
            obj.includes_confidentiality,
            obj.includes_termination,
            obj.includes_dispute_resolution
        ])
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 5px 10px; border-radius: 3px;">{} clauses</span>',
            count
        )
    clauses_count.short_description = 'Clauses'


@admin.register(TemplateScanLog)
class TemplateScanLogAdmin(admin.ModelAdmin):
    list_display = ['template', 'result', 'reason', 'scanned_at', 'task_id']
    list_filter = ['result', 'scanned_at']
    search_fields = ['template__name', 'task_id']
    readonly_fields = ['template', 'result', 'reason', 'scanned_at', 'task_id', 'scanned_by']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TemplateUsageLog)
class TemplateUsageLogAdmin(admin.ModelAdmin):
    list_display = ['template', 'action', 'user', 'created_at']
    list_filter = ['action', 'template__template_type', 'created_at']
    search_fields = ['template__name', 'user__username', 'document_reference']
    readonly_fields = ['template', 'user', 'action', 'document_reference', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
