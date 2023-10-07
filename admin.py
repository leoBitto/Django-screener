from django.contrib import admin
from .models import Company, Portfolio, StockInPortfolio


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ticker', 'sector', 'industry')
    search_fields = ('name', 'ticker', 'sector', 'industry')
    list_filter = ('sector', 'industry')
    readonly_fields = ('latest_update',)


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'cash_balance', 'stock_value', 'total_value')
    search_fields = ('name',)
    list_filter = ('start_date',)
    readonly_fields = ('stock_value', 'total_value', 'returns')


class StockInPortfolioAdmin(admin.ModelAdmin):
    list_display = ('company', 'related_portfolio', 'quantity', 'purchase_price', 'purchase_date',)
    search_fields = ('company__name', 'portfolio__name')
    list_filter = ('purchase_date',)
    readonly_fields = ('total_purchase_cost', 'unrealized_pnl', 'pmc')

admin.site.register(Company, CompanyAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(StockInPortfolio, StockInPortfolioAdmin)
