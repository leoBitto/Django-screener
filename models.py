from django.db import models
from django.conf import settings
import os

from django.core.files.storage import FileSystemStorage
import yfinance as yf
import pandas as pd
import numpy as np


ARCHIVE_PATH = str(settings.BASE_DIR) + "/archive/"
path_balancesheet = FileSystemStorage('/balancesheet')
path_income_statement = FileSystemStorage('/income_statement')
path_cash_flow = FileSystemStorage('/cash_flow')
path_history = FileSystemStorage('/history')

# Create your models here.
class Company(models.Model):

    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    
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
        

    def current_price(self):
        try:
            company = yf.Ticker(self.ticker)
            current_price = company.history(period="1d")["Close"].iloc[0]
            return current_price
        except Exception as e:
            # In caso di errori nel recupero del prezzo, restituisci None o un valore di default
            print(f"Error fetching current price for {self.name}: {e}")
            return None
        

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


    def historical_returns(self):
        try:
            history_path = os.path.join(ARCHIVE_PATH, "history", f"{self.ticker}.csv")
            df = pd.read_csv(history_path)
            
            if "Close" in df:
                prices = df["close"].tolist()
                returns = []

                for i in range(1, len(prices)):
                    daily_return = (prices[i] - prices[i - 1]) / prices[i - 1]
                    returns.append(daily_return)

                return returns
        except Exception as e:
            print(f"Error calculating historical returns for {self.name}: {e}")
        
        return []


    def calculate_standard_deviation(self):
        returns = self.historical_returns()
        if returns:
            return np.std(returns)
        return None


    def __str__(self):
        return self.name


