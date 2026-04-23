from django.contrib import admin
from .models import *

# Simple registration of all analytics models
admin.site.register(ReportTemplate)
admin.site.register(DashboardWidget)
admin.site.register(SalesAnalytics)
admin.site.register(InventoryAnalytics)
admin.site.register(ProfitabilityAnalytics)
admin.site.register(CustomerAnalytics)
admin.site.register(AuditLog)
