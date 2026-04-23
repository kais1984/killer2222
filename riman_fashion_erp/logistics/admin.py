from django.contrib import admin
from .models import *

# Simple registration of all logistics models
admin.site.register(WarehouseLocation)
admin.site.register(StockAllocation)
admin.site.register(Shipment)
admin.site.register(ShipmentItem)
admin.site.register(ShippingCarrier)
admin.site.register(ShipmentTracking)
admin.site.register(TrackingUpdate)
admin.site.register(ReturnRequest)
admin.site.register(PickingTask)
admin.site.register(PackingTask)
