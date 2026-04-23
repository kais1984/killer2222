from django.contrib import admin
from django.utils import timezone
from .models import (
    Client, Measurement, Appointment, ClientNote, 
    ClientPreference, ClientInteraction, Contract
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'client_type', 'status', 'outstanding_balance', 'created_at']
    list_filter = ['client_type', 'status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'last_purchase_date']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'phone_2')
        }),
        ('Classification', {
            'fields': ('client_type', 'status')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Financial', {
            'fields': ('total_purchases', 'total_rentals', 'outstanding_balance')
        }),
        ('Notes', {
            'fields': ('general_notes', 'preferences')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'last_purchase_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ['client', 'measured_date', 'bust', 'waist', 'height']
    list_filter = ['measured_date', 'client']
    search_fields = ['client__first_name', 'client__last_name']
    readonly_fields = ['measured_date']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client', 'appointment_type', 'scheduled_date', 'scheduled_time', 'status']
    list_filter = ['appointment_type', 'status', 'scheduled_date']
    search_fields = ['client__first_name', 'client__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ClientNote)
class ClientNoteAdmin(admin.ModelAdmin):
    list_display = ['client', 'title', 'note_type', 'created_at']
    list_filter = ['note_type', 'created_at']
    search_fields = ['client__first_name', 'client__last_name', 'title', 'content']
    readonly_fields = ['created_at']


@admin.register(ClientPreference)
class ClientPreferenceAdmin(admin.ModelAdmin):
    list_display = ['client', 'preferred_fit', 'typical_budget']
    search_fields = ['client__first_name', 'client__last_name']


@admin.register(ClientInteraction)
class ClientInteractionAdmin(admin.ModelAdmin):
    list_display = ['client', 'interaction_type', 'interaction_date']
    list_filter = ['interaction_type', 'interaction_date']
    search_fields = ['client__first_name', 'client__last_name', 'description']
    readonly_fields = ['interaction_date']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'client', 'contract_type', 'total_price', 'status', 'contract_date']
    list_filter = ['contract_type', 'status', 'contract_date']
    search_fields = ['contract_number', 'client__first_name', 'client__last_name', 'client__email', 'product__name', 'product__sku']
    readonly_fields = ['contract_number', 'created_at', 'created_by', 'approved_at', 'approved_by', 'invoicing_started_at']
    
    fieldsets = (
        ('Contract Information', {
            'fields': ('contract_number', 'contract_type', 'status')
        }),
        ('Client & Personnel', {
            'fields': ('client', 'sales_person')
        }),
        ('Product/Service', {
            'fields': ('product_specification', 'product')
        }),
        ('Timeline', {
            'fields': (
                'contract_date',
                'rental_start_date', 'rental_end_date',
                'production_start_date', 'production_end_date',
                'delivery_date'
            )
        }),
        ('Pricing & Payment', {
            'fields': (
                'total_price',
                'deposit_amount', 'deposit_due_date',
                'payment_schedule'
            )
        }),
        ('Terms', {
            'fields': ('notes', 'terms'),
            'classes': ('collapse',)
        }),
        ('Audit & Immutability', {
            'fields': (
                'created_at', 'created_by',
                'approved_at', 'approved_by',
                'invoicing_started_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_approved', 'mark_in_production', 'mark_ready', 'mark_completed']
    
    def mark_approved(self, request, queryset):
        updated = queryset.filter(status='draft').update(
            status='approved',
            approved_at=timezone.now(),
            approved_by=request.user
        )
        self.message_user(request, f'{updated} contracts marked as Approved')
    
    def mark_in_production(self, request, queryset):
        updated = queryset.filter(status='approved', contract_type__in=['custom_sale', 'custom_rent']).update(
            status='in_production'
        )
        self.message_user(request, f'{updated} contracts marked as In Production')
    
    def mark_ready(self, request, queryset):
        updated = queryset.filter(status__in=['approved', 'in_production']).update(
            status='ready'
        )
        self.message_user(request, f'{updated} contracts marked as Ready')
    
    def mark_completed(self, request, queryset):
        updated = queryset.filter(status__in=['ready']).update(
            status='completed'
        )
        self.message_user(request, f'{updated} contracts marked as Completed')
    
    mark_approved.short_description = "Mark selected contracts as Approved"
    mark_in_production.short_description = "Mark selected contracts as In Production"
    mark_ready.short_description = "Mark selected contracts as Ready"
    mark_completed.short_description = "Mark selected contracts as Completed"
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
