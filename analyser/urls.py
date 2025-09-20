"""
analyzer/urls.py

URL configuration for the 'analyzer' application.

Defines the routing for the API endpoint that handles contract analysis requests.
"""

from django.urls import path
from . import views


urlpatterns = [

    path('analyze/', views.analyze, name='analyze_contract'),
]