from django.db import models
from django.conf import settings
import os
from decimal import Decimal
from django.core.files.storage import FileSystemStorage
from datetime import datetime
import json
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


class Portfolio(models.Model):
    name = models.CharField(max_length=50)
    related_stocks = models.ManyToManyField('StockInPortfolio', blank=True)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField()  
    returns = models.TextField(blank=True)


    def calculate_roi(self):
        total_investment = sum(stock.purchase_price * stock.quantity for stock in self.stocks.all())
        
        if total_investment == 0:
            return 0  # Evita la divisione per zero
        
        current_value = self.stock_value
        roi = ((current_value - total_investment) / total_investment) * 100
        return roi

    def total_return(self):
        initial_value = self.total_value - self.cash_balance
        final_value = self.total_value
        
        if initial_value == 0:
            return 0  # Evita la divisione per zero
        
        return ((final_value - initial_value) / initial_value) * 100

    def average_annual_return(self):
        initial_value = self.total_value - self.cash_balance
        final_value = self.total_value
        years_passed = (datetime.now().date() - self.start_date).days / 365
        
        if initial_value == 0 or years_passed == 0:
            return 0  # Evita la divisione per zero
        
        return ((final_value - initial_value) / initial_value) / years_passed * 100
    
    def calculate_portfolio_risk(self):
        items = self.items.all()
        total_risk = 0
        for item in items:
            company_risk = item.company.calculate_standard_deviation()
            total_risk += (company_risk * item.quantity) ** 2
        portfolio_risk = np.sqrt(total_risk)
        return portfolio_risk

    def calculate_portfolio_returns(self):
        stocks = self.stocks.all()
        returns = []

        for i in range(1, len(stocks)):
            prev_stock = stocks[i - 1]
            current_stock = stocks[i]

            if prev_stock.total_value != 0:
                return_percentage = ((current_stock.total_value - prev_stock.total_value) / prev_stock.total_value) * 100
                returns.append(return_percentage)

        self.returns = json.dumps(returns)
        self.save()


    def __str__(self):
        return self.name


class StockInPortfolio(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    related_portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_date = models.DateField()

    def __str__(self):
        return f"{self.company.name} - {self.quantity}"

    @property
    def total_purchase_cost(self):
        if self.purchase_price is not None and self.purchase_commission is not None and self.quantity is not None:
            return (self.quantity * self.purchase_price) + self.purchase_commission
        else:
            return 0
        
    @property
    def unrealized_pnl(self):
        if self.company.current_price() is not None:
            current_price = Decimal(self.company.current_price())  # Converti in Decimal
            return (current_price - self.purchase_price - self.purchase_commission) * self.quantity
        return Decimal(0)

    def pmc(self):
        if self.quantity is not None:
            return self.total_purchase_cost / self.quantity if self.quantity > 0 else 0
        else:
            return 0

    def sell(self, quantity_to_sell):
        if self.quantity is not None and quantity_to_sell is not None:
            if quantity_to_sell <= self.quantity:
                self.quantity -= quantity_to_sell
                self.save()

                if self.quantity == 0:
                    self.delete()
                
                # Aggiorna il portafoglio
                self.related_portfolio.update_portfolio_values()

                return True
            else:
                return False
        else:
            return False  # Ritorna False se uno dei valori è None
        

    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)

