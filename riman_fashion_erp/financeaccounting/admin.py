"""
Finance Accounting Admin Configuration
"""

from django.contrib import admin
from financeaccounting.models import Account, JournalEntry, JournalEntryLine, FinancialReport


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin interface for Chart of Accounts"""
    list_display = ('account_code', 'account_name', 'account_type', 'account_subtype', 'is_active')
    list_filter = ('account_type', 'is_active')
    search_fields = ('account_code', 'account_name')
    fieldsets = (
        ('Basic Information', {
            'fields': ('account_code', 'account_name', 'account_type', 'account_subtype')
        }),
        ('Details', {
            'fields': ('description', 'is_active')
        }),
    )
    readonly_fields = ('id', 'created_at')


class JournalEntryLineInline(admin.TabularInline):
    """Inline admin for journal entry lines"""
    model = JournalEntryLine
    extra = 1
    fields = ('account', 'line_type', 'amount', 'description')


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """Admin interface for Journal Entries"""
    list_display = ('journal_number', 'entry_type', 'entry_date', 'created_at')
    list_filter = ('entry_type', 'entry_date')
    search_fields = ('journal_number', 'description')
    inlines = [JournalEntryLineInline]
    fieldsets = (
        ('Entry Information', {
            'fields': ('journal_number', 'entry_type', 'entry_date', 'description')
        }),
        ('References', {
            'fields': ('sale_id', 'payment_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('journal_number', 'id', 'created_at', 'created_by')
    
    def get_readonly_fields(self, request, obj=None):
        """Make journal entries immutable once created"""
        if obj:  # Editing an existing object
            return self.readonly_fields + ('entry_type', 'entry_date', 'description')
        return self.readonly_fields


# StockMovement is now in inventory app - no longer duplicate here


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    """Admin interface for Financial Reports"""
    list_display = ('report_type', 'report_date', 'generated_by', 'generated_at')
    list_filter = ('report_type', 'report_date')
    fieldsets = (
        ('Report Information', {
            'fields': ('report_type', 'report_date', 'report_data')
        }),
        ('Metadata', {
            'fields': ('generated_by', 'generated_at', 'id'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('id', 'generated_at', 'report_data')
