from django import forms
from .models import Portfolio, PortfolioAsset, Transaction
from risk_management.models import Asset
from django.core.exceptions import ValidationError
from decimal import Decimal

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise ValidationError("Portfolio name must be at least 3 characters long.")
        return name

class PortfolioAssetForm(forms.ModelForm):
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = PortfolioAsset
        fields = ['asset', 'quantity', 'purchase_price', 'purchase_date']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.000001'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_purchase_price(self):
        price = self.cleaned_data['purchase_price']
        if price <= 0:
            raise ValidationError("Purchase price must be greater than zero.")
        return price

class TransactionForm(forms.ModelForm):
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Transaction
        fields = ['asset', 'transaction_type', 'quantity', 'price', 'transaction_date']
        widgets = {
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.000001'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        quantity = cleaned_data.get('quantity')
        price = cleaned_data.get('price')
        
        if quantity is not None and quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        
        if price is not None and price <= 0:
            raise ValidationError("Price must be greater than zero.")
        
        if transaction_type == 'SELL':
            portfolio = self.initial.get('portfolio')
            asset = cleaned_data.get('asset')
            if portfolio and asset:
                try:
                    portfolio_asset = PortfolioAsset.objects.get(portfolio=portfolio, asset=asset)
                    if quantity > portfolio_asset.quantity:
                        raise ValidationError(f"Cannot sell more than the available quantity. Available: {portfolio_asset.quantity}")
                except PortfolioAsset.DoesNotExist:
                    raise ValidationError("You don't own this asset in the selected portfolio.")
        
        return cleaned_data

class AIInvestmentAdviceForm(forms.Form):
    RISK_TOLERANCE_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    INVESTMENT_HORIZON_CHOICES = [
        ('short', 'Short-term (0-2 years)'),
        ('medium', 'Medium-term (2-5 years)'),
        ('long', 'Long-term (5+ years)'),
    ]
    
    risk_tolerance = forms.ChoiceField(choices=RISK_TOLERANCE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    investment_horizon = forms.ChoiceField(choices=INVESTMENT_HORIZON_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    investment_goals = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    preferred_sectors = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))
    monthly_investment = forms.DecimalField(min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    esg_preference = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate sectors from Asset model
        self.fields['preferred_sectors'].choices = [(sector, sector) for sector in Asset.objects.values_list('sector', flat=True).distinct()]

    def clean_monthly_investment(self):
        monthly_investment = self.cleaned_data['monthly_investment']
        if monthly_investment < Decimal('10.00'):
            raise ValidationError("Monthly investment should be at least $10.00")
        return monthly_investment