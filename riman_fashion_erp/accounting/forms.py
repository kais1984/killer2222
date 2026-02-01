from django import forms
from accounting.models import ChartOfAccounts, JournalEntry, JournalEntryLine, Expense


class AccountForm(forms.ModelForm):
    class Meta:
        model = ChartOfAccounts
        fields = ['account_code', 'account_name', 'account_type', 'account_category', 'description', 'opening_balance']
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Code'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Name'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'account_category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Opening Balance', 'step': '0.01'}),
        }


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['entry_date', 'reference_number', 'description', 'status']
        widgets = {
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference Number'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class JournalEntryLineForm(forms.ModelForm):
    class Meta:
        model = JournalEntryLine
        fields = ['account', 'debit_amount', 'credit_amount', 'description']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-control'}),
            'debit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'credit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ExpenseForm(forms.ModelForm):
    """Form for creating/editing expenses (Phase 3)"""
    
    class Meta:
        model = Expense
        fields = ['expense_date', 'expense_type', 'description', 'amount', 'account', 
                  'supplier', 'reference_number', 'receipt_file', 'notes']
        widgets = {
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expense_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Expense description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Amount'}),
            'account': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier/Vendor name'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice/Receipt #'}),
            'receipt_file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        account = cleaned_data.get('account')
        
        if amount and amount <= 0:
            self.add_error('amount', 'Amount must be greater than 0')
        
        if not account:
            self.add_error('account', 'Expense account is required')
        elif account.account_type != 'expense':
            self.add_error('account', 'Selected account must be an expense account')
        
        return cleaned_data


class ExpenseSubmitForm(forms.Form):
    """Form for submitting expense for approval"""
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Submission notes (optional)'}),
        required=False
    )


class ExpenseApprovalForm(forms.Form):
    """Form for approving/rejecting expenses"""
    
    DECISION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Approval notes'}),
        required=False
    )
