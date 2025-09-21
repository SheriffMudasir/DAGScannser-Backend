"""
analyzer/urls.py

URL configuration for the 'analyzer' application.
"""

from django.urls import path
from . import views


urlpatterns = [

    path('analyze/', views.analyze, name='analyze_contract'),
]