from django.contrib import admin
from django.urls import path
from . import views
from .helpers import tasks

app_name = 'screener'
urlpatterns = [
    path('', views.index, name="index"),
    path('company/', views.company, name='company'),
    path('update/', views.update, name="update"),
    
    path('update_db/', tasks.update_stock_data, name="update_db"),  #URL per l'aggiornamento automatico
]
