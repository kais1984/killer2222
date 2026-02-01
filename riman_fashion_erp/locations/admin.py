from django.contrib import admin
from .models import *

# Simple registration of all locations models
admin.site.register(Branch)
admin.site.register(BranchInventory)
admin.site.register(InterBranchTransfer)
admin.site.register(TransferItem)
admin.site.register(BranchSales)
admin.site.register(BranchExpense)
