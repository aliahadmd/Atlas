from django import forms
from .models import Portfolio, PortfolioAsset, Transaction

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PortfolioAssetForm(forms.ModelForm):
    class Meta:
        model = PortfolioAsset
        fields = ['asset', 'quantity', 'purchase_price', 'purchase_date']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['asset', 'transaction_type', 'quantity', 'price', 'transaction_date']
        widgets = {
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        quantity = cleaned_data.get('quantity')
        
        if transaction_type == 'SELL' and quantity and quantity <= 0:
            raise forms.ValidationError("Quantity must be positive for sell transactions.")
        
        return cleaned_data