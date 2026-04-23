"""
Serializers for all models
"""

from rest_framework import serializers
from suppliers.models import Supplier, PurchaseInvoice, PurchaseInvoiceItem
from inventory.models import Product, Warehouse, StockMovement
from sales.models import Order, Invoice, Promotion
from rentals.models import RentalAgreement
from crm.models import Client
from accounting.models import ChartOfAccounts, Income, Expense

# Supplier Serializers
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class PurchaseInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoiceItem
        fields = '__all__'

class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    items = PurchaseInvoiceItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseInvoice
        fields = '__all__'

# Inventory Serializers
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class StockMovementSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = '__all__'

# Sales Serializers
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'

# Rental Serializers
class RentalAgreementSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = RentalAgreement
        fields = '__all__'

# CRM Serializers
class ClientSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    class Meta:
        model = Client
        fields = '__all__'

# Accounting Serializers
class ChartOfAccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccounts
        fields = '__all__'

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
