from django.contrib import admin
from .models import *

# Simple registration of all barcodes models
admin.site.register(BarcodeTemplate)
admin.site.register(ProductBarcode)
admin.site.register(ProductBatch)
admin.site.register(ProductSerial)
admin.site.register(BarcodeLabel)
admin.site.register(BarcodeScan)
