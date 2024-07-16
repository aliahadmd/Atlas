from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F
from .models import Portfolio, PortfolioAsset, PortfolioPerformance, Transaction

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'total_value', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username', 'description')
    list_filter = ('created_at', 'updated_at', 'owner')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'description', 'owner')}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def total_value(self, obj):
        total = PortfolioAsset.objects.filter(portfolio=obj).aggregate(
            total=Sum(F('quantity') * F('asset__value'))
        )['total'] or 0
        return f"${total:.2f}"
    total_value.short_description = 'Total Value'

@admin.register(PortfolioAsset)
class PortfolioAssetAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'asset', 'quantity', 'purchase_price', 'current_value', 'purchase_date')
    search_fields = ('portfolio__name', 'asset__name', 'asset__symbol')
    list_filter = ('purchase_date', 'portfolio', 'asset')
    readonly_fields = ('current_value',)

    def current_value(self, obj):
        return f"${obj.quantity * obj.asset.value:.2f}"
    current_value.short_description = 'Current Value'

@admin.register(PortfolioPerformance)
class PortfolioPerformanceAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'date', 'total_value', 'daily_return_display', 'cumulative_return_display')
    search_fields = ('portfolio__name',)
    list_filter = ('date', 'portfolio')
    date_hierarchy = 'date'

    def daily_return_display(self, obj):
        return self.format_return(obj.daily_return)
    daily_return_display.short_description = 'Daily Return'

    def cumulative_return_display(self, obj):
        return self.format_return(obj.cumulative_return)
    cumulative_return_display.short_description = 'Cumulative Return'

    def format_return(self, value):
        color = 'green' if value >= 0 else 'red'
        return format_html('<span style="color: {};">{:.2f}%</span>', color, value * 100)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'asset', 'transaction_type', 'quantity', 'price', 'total_value', 'transaction_date')
    search_fields = ('portfolio__name', 'asset__name', 'asset__symbol')
    list_filter = ('transaction_type', 'transaction_date', 'portfolio', 'asset')
    date_hierarchy = 'transaction_date'

    def total_value(self, obj):
        return f"${obj.quantity * obj.price:.2f}"
    total_value.short_description = 'Total Value'

    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
        writer = csv.writer(response)
        writer.writerow(['Portfolio', 'Asset', 'Type', 'Quantity', 'Price', 'Total Value', 'Date'])

        for obj in queryset:
            writer.writerow([
                obj.portfolio.name,
                obj.asset.name,
                obj.get_transaction_type_display(),
                obj.quantity,
                obj.price,
                obj.quantity * obj.price,
                obj.transaction_date
            ])

        return response
    export_as_csv.short_description = "Export selected transactions as CSV"