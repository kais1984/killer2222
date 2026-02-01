from django.contrib import admin
from .models import *

# Simple registration of all production models
admin.site.register(BillOfMaterials)
admin.site.register(BOMComponent)
admin.site.register(ProductionStage)
admin.site.register(WorkOrder)
admin.site.register(WorkOrderStage)
admin.site.register(LaborCostAllocation)
admin.site.register(ProductionMetrics)
