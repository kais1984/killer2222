from django.contrib import admin
from .models import *

# Simple registration of all workflows models
admin.site.register(ApprovalRule)
admin.site.register(ApprovalLevel)
admin.site.register(ApprovalRequest)
admin.site.register(Approval)
admin.site.register(AuditTrail)
