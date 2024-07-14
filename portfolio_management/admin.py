from django.contrib import admin
from .models import Portfolio, PortfolioAsset, PortfolioPerformance, Transaction

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('created_at', 'updated_at')

@admin.register(PortfolioAsset)
class PortfolioAssetAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'asset', 'quantity', 'purchase_price', 'purchase_date')
    search_fields = ('portfolio__name', 'asset__name')
    list_filter = ('purchase_date',)

@admin.register(PortfolioPerformance)
class PortfolioPerformanceAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'date', 'total_value', 'daily_return', 'cumulative_return')
    search_fields = ('portfolio__name',)
    list_filter = ('date',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'asset', 'transaction_type', 'quantity', 'price', 'transaction_date')
    search_fields = ('portfolio__name', 'asset__name')
    list_filter = ('transaction_type', 'transaction_date')