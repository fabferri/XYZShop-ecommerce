"""
Set All Products Online
Updates every product in the database to is_online=True, making the
entire catalog visible to customers on the storefront.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product

def set_products_online():
    """Set all existing products to online status"""
    print("Setting all existing products to ONLINE status...")
    print("=" * 60)
    
    # Update all products to be online
    updated = Product.objects.all().update(is_online=True)
    
    print(f"SUCCESS: Set {updated} products to ONLINE status")
    print("=" * 60)
    print("All existing products are now visible to customers")
    print("New products added in admin will be in warehouse (offline) by default")
    print("   Administrators can move them online using the admin panel")

if __name__ == '__main__':
    set_products_online()
