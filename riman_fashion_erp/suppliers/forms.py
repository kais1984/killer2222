from django import forms
from suppliers.models import Supplier, PurchaseInvoice


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'category', 'contact_person', 'email', 'phone', 'address', 'city', 'country']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        }


class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        fields = ['invoice_number', 'supplier', 'invoice_date', 'due_date', 'total_amount', 'status', 'notes']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice Number'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Amount', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
        }
