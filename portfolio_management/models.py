from django.db import models
from django.conf import settings

class Portfolio(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio_assets')
    asset = models.ForeignKey('risk_management.Asset', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)
    purchase_date = models.DateField()

    class Meta:
        unique_together = ('portfolio', 'asset')

    def __str__(self):
        return f"{self.asset.name} in {self.portfolio.name}"

class PortfolioPerformance(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='performances')
    date = models.DateField()
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    daily_return = models.DecimalField(max_digits=8, decimal_places=4)
    cumulative_return = models.DecimalField(max_digits=8, decimal_places=4)

    class Meta:
        unique_together = ('portfolio', 'date')

    def __str__(self):
        return f"{self.portfolio.name} performance on {self.date}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    asset = models.ForeignKey('risk_management.Asset', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField()
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.quantity} {self.asset.name} for {self.portfolio.name}"