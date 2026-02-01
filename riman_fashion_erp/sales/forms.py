from django import forms
from sales.models import Promotion, Sale, Invoice, Payment


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add any notes for this sale'}),
        }


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['name', 'code', 'description', 'discount_type', 'discount_value', 'start_date', 'end_date', 'max_uses', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'discount_type': forms.Select(attrs={'class': 'form-control'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_uses': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class InvoiceForm(forms.ModelForm):
    """Form for creating/editing invoices"""
    
    class Meta:
        model = Invoice
        fields = ['sale', 'contract', 'invoice_type', 'subtotal', 'tax_amount', 'due_date']
        widgets = {
            'sale': forms.Select(attrs={'class': 'form-control'}),
            'contract': forms.Select(attrs={'class': 'form-control'}),
            'invoice_type': forms.Select(attrs={'class': 'form-control'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        sale = cleaned_data.get('sale')
        contract = cleaned_data.get('contract')
        
        # One required
        if not sale and not contract:
            raise forms.ValidationError("Invoice must have either a Sale or a Contract")
        
        # Not both
        if sale and contract:
            raise forms.ValidationError("Invoice cannot have both Sale and Contract")
        
        return cleaned_data


class InvoiceDepositForm(forms.ModelForm):
    """Specific form for deposit invoices"""
    
    class Meta:
        model = Invoice
        fields = ['contract', 'subtotal', 'tax_amount', 'due_date']
        widgets = {
            'contract': forms.Select(attrs={'class': 'form-control'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-set invoice_type
        if self.instance and self.instance.pk:
            self.instance.invoice_type = 'deposit'


class PaymentForm(forms.ModelForm):
    """Form for recording payments"""
    
    class Meta:
        model = Payment
        fields = ['sale', 'amount', 'payment_method', 'payment_date', 'reference']
        widgets = {
            'sale': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Check#, transaction ID, etc.'}),
        }

