from django.contrib import admin
from .models import (
    Category, Collection, Product, ProductImage, 
    Warehouse, StockLocation, StockMovement, LowStockAlert, RentalReservation
)


@admin.register(RentalReservation)
class RentalReservationAdmin(admin.ModelAdmin):
    list_display = ['contract', 'product', 'quantity_reserved', 'rental_start_date', 'rental_end_date', 'status']
    list_filter = ['status', 'rental_start_date', 'rental_end_date']
    search_fields = ['contract__contract_number', 'contract__client__first_name', 'contract__client__last_name', 'product__sku', 'product__name']
    readonly_fields = ['created_at', 'returned_at', 'returned_by']
    
    fieldsets = (
        ('Reservation Details', {
            'fields': ('contract', 'product', 'quantity_reserved')
        }),
        ('Rental Period', {
            'fields': ('rental_start_date', 'rental_end_date')
        }),
        ('Status', {
            'fields': ('status', 'returned_at', 'returned_by')
        }),
        ('Audit', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_active', 'mark_returned']
    
    def mark_active(self, request, queryset):
        updated = queryset.filter(status='reserved').update(status='active')
        self.message_user(request, f'{updated} reservations marked as Active')
    
    def mark_returned(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='active').update(
            status='returned',
            returned_at=timezone.now(),
            returned_by=request.user
        )
        self.message_user(request, f'{updated} reservations marked as Returned')
    
    mark_active.short_description = "Mark as Active (customer has product)"
    mark_returned.short_description = "Mark as Returned (customer returned product)"
