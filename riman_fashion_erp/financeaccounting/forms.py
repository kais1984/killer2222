"""
Finance Accounting Forms
"""

from django import forms
from financeaccounting.models import Account, JournalEntry, JournalEntryLine
from inventory.models import StockMovement


class AccountForm(forms.ModelForm):
    """Form for creating/editing accounts"""
    class Meta:
        model = Account
        fields = ['account_code', 'account_name', 'account_type', 'account_subtype', 'description', 'is_active']
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1100'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account name'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'account_subtype': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account subtype'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class JournalEntryForm(forms.ModelForm):
    """Form for creating journal entries"""
    class Meta:
        model = JournalEntry
        fields = ['entry_type', 'entry_date', 'description']
        widgets = {
            'entry_type': forms.Select(attrs={'class': 'form-control'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Journal entry description'}),
        }


class JournalEntryLineForm(forms.ModelForm):
    """Form for adding lines to journal entries"""
    class Meta:
        model = JournalEntryLine
        fields = ['account', 'line_type', 'amount', 'description']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-control'}),
            'line_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Amount'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Line description'}),
        }


class StockMovementForm(forms.ModelForm):
    """Form for recording stock movements"""
    class Meta:
        model = StockMovement
        fields = ['product', 'from_warehouse', 'to_warehouse', 'movement_type', 'quantity', 'reference_number', 'reference_type', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'from_warehouse': forms.Select(attrs={'class': 'form-control'}),
            'to_warehouse': forms.Select(attrs={'class': 'form-control'}),
            'movement_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity', 'min': '1'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference (PO#, etc.)'}),
            'reference_type': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }
