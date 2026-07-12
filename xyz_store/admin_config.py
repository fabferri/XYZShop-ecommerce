"""
Admin App Configuration
Registers CustomAdminSite as the default Django admin site.
"""
from django.contrib.admin.apps import AdminConfig

class CustomAdminConfig(AdminConfig):
    default_site = 'xyz_store.admin.CustomAdminSite'
