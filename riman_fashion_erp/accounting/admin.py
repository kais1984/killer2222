from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from accounting.models import (
    ChartOfAccounts, JournalEntry, JournalEntryLine, 
    Income, Expense, Asset, Liability, FinancialPeriod
)


@admin.register(ChartOfAccounts)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_code', 'account_name', 'account_type', 'account_category', 'current_balance', 'is_active']
    list_filter = ['account_type', 'account_category', 'is_active']
    search_fields = ['account_code', 'account_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('account_code', 'account_name', 'account_type', 'account_category')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Balances', {
            'fields': ('opening_balance', 'current_balance')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Audit Trail', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 0
    readonly_fields = ['account', 'debit_amount', 'credit_amount']
    can_delete = False


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'entry_date', 'description', 'status', 'total_debit', 'total_credit']
    list_filter = ['status', 'entry_date']
    search_fields = ['reference_number', 'description']
    readonly_fields = ['created_at', 'approved_at']
    inlines = [JournalEntryLineInline]
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('entry_date', 'reference_number', 'description', 'status')
        }),
        ('Amounts', {
            'fields': ('total_debit', 'total_credit')
        }),
        ('Approval', {
            'fields': ('created_by', 'approved_by', 'created_at', 'approved_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['income_date', 'get_income_type_display', 'description', 'amount']
    list_filter = ['income_type', 'income_date']
    search_fields = ['description', 'reference_number']
    readonly_fields = ['created_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Expense admin with status workflow (Phase 3)"""
    list_display = ['expense_number', 'expense_date', 'get_expense_type_display', 'amount', 'status_badge', 'supplier']
    list_filter = ['status', 'expense_type', 'expense_date', 'is_posted']
    search_fields = ['expense_number', 'description', 'supplier', 'reference_number']
    readonly_fields = ['expense_number', 'created_at', 'updated_at', 'submitted_at', 'approved_at', 'posted_at']
    
    fieldsets = (
        ('Expense Information', {
            'fields': ('expense_number', 'expense_date', 'expense_type', 'description')
        }),
        ('Financial Details', {
            'fields': ('amount', 'account', 'supplier', 'reference_number', 'receipt_file')
        }),
        ('Status & Workflow', {
            'fields': ('status', 'is_posted', 'gl_posted')
        }),
        ('Approval Trail', {
            'fields': ('submitted_by', 'submitted_at', 'approved_by', 'approved_at', 'posted_by', 'posted_at'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Color-coded status badge"""
        colors = {
            'draft': '#6c757d',      # Gray
            'submitted': '#0d6efd',   # Blue
            'approved': '#0dcaf0',    # Cyan
            'posted': '#198754',      # Green
            'rejected': '#dc3545',    # Red
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_readonly_fields(self, request, obj=None):
        """Make fields read-only if expense is posted"""
        if obj and obj.is_posted:
            return list(self.readonly_fields) + ['amount', 'account', 'supplier', 'reference_number', 'receipt_file', 'expense_date', 'expense_type', 'description']
        return self.readonly_fields
    
    actions = ['approve_expenses', 'reject_expenses', 'post_to_gl']
    
    def approve_expenses(self, request, queryset):
        """Bulk approve expenses"""
        updated = queryset.filter(status='submitted').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} expenses approved.')
    approve_expenses.short_description = 'Approve selected expenses'
    
    def reject_expenses(self, request, queryset):
        """Bulk reject expenses"""
        updated = queryset.filter(status__in=['draft', 'submitted']).update(status='rejected')
        self.message_user(request, f'{updated} expenses rejected.')
    reject_expenses.short_description = 'Reject selected expenses'
    
    def post_to_gl(self, request, queryset):
        """Bulk post expenses to GL"""
        from financeaccounting.services import ExpenseAccountingService
        from django.contrib import messages as dj_messages
        from django.utils import timezone
        
        posted_count = 0
        for expense in queryset.filter(status='approved', is_posted=False):
            try:
                expense.post_to_gl(request.user)
                posted_count += 1
            except Exception as e:
                dj_messages.error(request, f"Failed to post {expense.expense_number}: {str(e)}")
        
        if posted_count > 0:
            dj_messages.success(request, f'{posted_count} expenses posted to GL.')
    post_to_gl.short_description = 'Post selected expenses to GL'


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_name', 'asset_type', 'acquisition_cost', 'accumulated_depreciation', 'current_value']
    list_filter = ['asset_type', 'purchase_date', 'is_active']
    search_fields = ['asset_name', 'description']
    readonly_fields = ['created_at', 'calculate_book_value']


@admin.register(Liability)
class LiabilityAdmin(admin.ModelAdmin):
    list_display = ['liability_name', 'liability_type', 'principal_amount', 'current_amount', 'due_date']
    list_filter = ['liability_type', 'is_paid_off']
    search_fields = ['liability_name', 'description']


@admin.register(FinancialPeriod)
class FinancialPeriodAdmin(admin.ModelAdmin):
    list_display = ['period_name', 'period_start', 'period_end', 'status', 'net_profit_loss']
    list_filter = ['status', 'period_start']
    readonly_fields = ['locked_at', 'closed_at']
