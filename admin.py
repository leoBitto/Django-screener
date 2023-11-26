from django.contrib import admin
from .models import Company

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ticker', 'sector', 'industry')
    search_fields = ('name', 'ticker', 'sector', 'industry')
    list_filter = ('sector', 'industry')
    readonly_fields = ('latest_update',)


admin.site.register(Company, CompanyAdmin)

