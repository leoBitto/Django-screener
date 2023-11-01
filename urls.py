from django.contrib import admin
from django.urls import path
from . import views
from .helpers import tasks

app_name = 'screener'
urlpatterns = [
    path('', views.index, name="index"),
    path('company/', views.company, name='company'),
    path('update/', views.update, name="update"),
    
    path('portfolio_details/<int:pk>/', views.portfolio_details, name="portfolio_details"),
    path('manage_stock/<int:pk>/', views.manage_stock, name='manage_stock'),
    path('create_portfolio/', views.create_portfolio, name="create_portfolio"),
    path('eliminate_portfolio/<int:pk>/', views.eliminate_portfolio, name="eliminate_portfolio"),
    path('portfolio/<int:pk>/manage_cash/', views.manage_cash, name='manage_cash'),



    path('update_db/', tasks.update_stock_data, name="update_db"),  #URL per l'aggiornamento automatico
]
