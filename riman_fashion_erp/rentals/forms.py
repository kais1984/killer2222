from django import forms
from rentals.models import RentalAgreement


class RentalForm(forms.ModelForm):
    class Meta:
        model = RentalAgreement
        fields = ['rental_number', 'client', 'rental_date', 'return_date', 'daily_rate', 'number_of_days', 'status']
        widgets = {
            'rental_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rental Number'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'rental_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'daily_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Daily Rate', 'step': '0.01'}),
            'number_of_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of Days'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
