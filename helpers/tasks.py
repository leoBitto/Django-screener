# tasks.py

from celery import shared_task
from django.utils import timezone

@shared_task
def update_stock_data():
    # Logic to update stock data (utilizza la tua logica attuale)
    # Assicurati di avere un metodo per recuperare l'elenco delle aziende

    companies = Company.objects.all()

    for company in companies:
        # Aggiorna i dati dell'azienda
        update_object(company.ticker)

    # Aggiorna anche i conti economici alla fine dell'anno
    if timezone.now().month == 12 and timezone.now().day == 31:
        for company in companies:
            update_financial_statements(company.ticker)
