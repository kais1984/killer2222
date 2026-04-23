from django.contrib import admin
from .models import *

# Simple registration of all quality models
admin.site.register(QualityChecklistTemplate)
admin.site.register(ChecklistItem)
admin.site.register(InspectionRecord)
admin.site.register(InspectionChecklistResult)
admin.site.register(DefectLog)
admin.site.register(QualityMetrics)
admin.site.register(ComplianceChecklist)
