from django import forms
from crm.models import Client, ClientInteraction, Contract
from inventory.models import Product


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone', 'client_type', 'address', 'city', 'state', 'country']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'client_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        }


class ClientInteractionForm(forms.ModelForm):
    class Meta:
        model = ClientInteraction
        fields = ['client', 'interaction_type', 'description', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'interaction_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
        }


class ContractForm(forms.ModelForm):
    """Form for creating and editing contracts"""
    
    class Meta:
        model = Contract
        fields = [
            'contract_type', 'client', 'sales_person',
            'product_specification', 'product',
            'contract_date', 'rental_start_date', 'rental_end_date',
            'production_start_date', 'production_end_date', 'delivery_date',
            'total_price', 'deposit_amount', 'deposit_due_date',
            'payment_schedule', 'notes', 'terms'
        ]
        widgets = {
            'contract_type': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'sales_person': forms.Select(attrs={'class': 'form-control', 'required': False}),
            'product_specification': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed product/service specifications'}),
            'product': forms.Select(attrs={'class': 'form-control', 'required': False}),
            'contract_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rental_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
            'rental_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
            'production_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
            'production_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Total contract price'}),
            'deposit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Deposit amount'}),
            'deposit_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
            'payment_schedule': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '[{"date": "2026-02-01", "amount": 5000, "description": "Milestone 1"}]'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
            'terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Custom contract terms and conditions'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.can_edit() is False:
            # Make fields read-only if contract is being invoiced
            for field_name in self.fields:
                self.fields[field_name].disabled = True
