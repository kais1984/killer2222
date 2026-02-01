from django.contrib import admin
from .models import *

# Simple registration of all finance models
admin.site.register(BudgetYear)
admin.site.register(BudgetCategory)
admin.site.register(Budget)
admin.site.register(FixedAsset)
admin.site.register(Depreciation)
admin.site.register(CashFlowProjection)
admin.site.register(PayrollEmployee)
admin.site.register(PayrollDeduction)
admin.site.register(Payroll)
admin.site.register(PayrollDetail)
admin.site.register(TaxConfiguration)
