from django import forms
from inventory.models import Product, StockMovement, Warehouse, ProductImage


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'description', 'dress_type', 'category', 'collection', 'size', 'color', 'material', 'availability', 'quantity_in_stock', 'cost_price', 'sale_price', 'rental_price_per_day']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'dress_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'collection': forms.Select(attrs={'class': 'form-control'}),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'material': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Material'}),
            'availability': forms.Select(attrs={'class': 'form-control'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock Quantity'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cost Price', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sale Price', 'step': '0.01'}),
            'rental_price_per_day': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Rental Price per Day', 'step': '0.01'}),
        }


class ProductImageForm(forms.ModelForm):
    """Form for uploading product photos"""
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary', 'order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image description'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'quantity', 'movement_type', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'movement_type': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
        }


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location_type', 'address', 'city', 'capacity', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Warehouse Name'}),
            'location_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacity (units)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
