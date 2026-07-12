"""
Orders App Configuration
Connects the orders signal handlers on app ready.
"""
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    
    def ready(self):
        import orders.signals
