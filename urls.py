from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name="index"),
    path('company/', views.company, name='company'),
    path('update/', views.update, name="update"),
    
]
