from django.db import models
from django.conf import settings
import os
from django.core.files.storage import FileSystemStorage

ARCHIVE_PATH = str(settings.BASE_DIR) + "/archive/"
path_balancesheet = FileSystemStorage('/balancesheet')
path_income_statement = FileSystemStorage('/income_statement')
path_cash_flow = FileSystemStorage('/cash_flow')
path_history = FileSystemStorage('/history')

# Create your models here.
class Company(models.Model):

    ticker = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    
    sector = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    
    phone = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    
    summary = models.TextField(blank=True, null=True)
    employees = models.IntegerField(blank=True, null=True)

    balancesheet = models.FileField(upload_to = path_balancesheet, blank=True, null=True)
    income_statement = models.FileField(upload_to = path_income_statement, blank=True, null=True)
    cash_flow = models.FileField(upload_to = path_cash_flow, blank=True, null=True)
    history = models.FileField(upload_to=path_history, blank=True, null=True)

    latest_update = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural="Companies"
        

    def delete(self):
        # delete the files after checking if they exist
        if os.path.exists(ARCHIVE_PATH + "balancesheet/" + self.ticker + ".csv"):
            os.remove(ARCHIVE_PATH + "balancesheet/" + self.ticker + ".csv")
        if os.path.exists(ARCHIVE_PATH + "cashflow/" + self.ticker + ".csv"):
            os.remove(ARCHIVE_PATH + "cashflow/" + self.ticker + ".csv")
        if os.path.exists(ARCHIVE_PATH + "history/" + self.ticker + ".csv"):
            os.remove(ARCHIVE_PATH + "history/" + self.ticker + ".csv")
        if os.path.exists(ARCHIVE_PATH + "income_statement/" + self.ticker + ".csv"):
            os.remove(ARCHIVE_PATH + "income_statement/" + self.ticker + ".csv")

        super(Company, self).delete()


    def __str__(self):
        return self.name
