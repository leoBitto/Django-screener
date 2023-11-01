from django.contrib import admin
from .models import Company, Portfolio, StockInPortfolio, StockTransaction

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ticker', 'sector', 'industry')
    search_fields = ('name', 'ticker', 'sector', 'industry')
    list_filter = ('sector', 'industry')
    readonly_fields = ('latest_update',)

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'cash_balance', 'stock_value', 'total_value')
    search_fields = ('name',)
    list_filter = ('start_date',)
    readonly_fields = ('stock_value', 'total_value',)

class StockInPortfolioAdmin(admin.ModelAdmin):
    list_display = ('company', 'related_portfolio', 'quantity', 'price')
    search_fields = ('company__name', 'related_portfolio__name')

class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('stock', 'transaction_type', 'quantity', 'price', 'commission', 'transaction_date')
    search_fields = ('stock__company__name', 'transaction_type')
    list_filter = ('transaction_date',)

admin.site.register(Company, CompanyAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(StockInPortfolio, StockInPortfolioAdmin)
admin.site.register(StockTransaction, StockTransactionAdmin)

