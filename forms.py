from django import forms
from .models import Company

class TransactionStockForm(forms.Form):
    company = forms.ModelChoiceField(queryset=Company.objects.all())
    quantity = forms.IntegerField()
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    commission = forms.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))  # Aggiunto widget
    transaction_type = forms.ChoiceField(choices=[('BUY', 'Buy'), ('SELL', 'Sell')])


class ManageCashForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = forms.ChoiceField(choices=[('DEPOSIT', 'Deposit'), ('WITHDRAW', 'Withdraw')])
    commission = forms.DecimalField(max_digits=10, decimal_places=2)