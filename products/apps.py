"""
Products App Configuration
Connects the products signal handlers on app ready.
"""
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    
    def ready(self):
        import products.signals  # noqa
