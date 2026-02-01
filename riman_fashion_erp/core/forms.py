from django import forms
from core.models import CompanySettings


class CompanySettingsForm(forms.ModelForm):
    """Form for updating company settings including logo"""
    
    class Meta:
        model = CompanySettings
        fields = [
            'company_name',
            'logo',
            'brand_color',
            'accent_color',
            'phone',
            'email',
            'address',
            'city',
            'state',
            'country',
            'postal_code',
            'currency_symbol',
            'currency_code',
            'tax_type',
            'tax_rate',
            'invoice_prefix',
            'invoice_next_number',
            'invoice_footer',
            'financial_year_start',
            'low_stock_threshold',
            # Document upload settings
            'upload_max_size',
            'allowed_extensions',
            'enforce_mime',
            'use_s3',
            'virus_scan',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'brand_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'accent_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '$'}),
            'currency_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'tax_type': forms.Select(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '10.00'}),
            'invoice_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INV-'}),
            'invoice_next_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1000'}),
            'invoice_footer': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'financial_year_start': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM-DD'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10'}),
            'upload_max_size': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Bytes'}),
            'allowed_extensions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'pdf,docx,doc,xlsx,xls,html,txt'}),
            'enforce_mime': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'use_s3': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'virus_scan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
