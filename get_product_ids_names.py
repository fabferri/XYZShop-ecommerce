"""
Get Product IDs and Names
Retrieves and displays all product IDs and names from the database,
ordered by ID. Useful for looking up specific products.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product

def get_product_ids_names():
    """Retrieve all product IDs and names"""
    products = Product.objects.all().order_by('id')
    
    if not products.exists():
        print("No products found in the database.")
        return
    
    print("=" * 70)
    print(f"{'ID':<8} {'Product Name':<60}")
    print("=" * 70)
    
    for product in products:
        print(f"{product.id:<8} {product.name:<60}")
    
    print("=" * 70)
    print(f"Total products: {products.count()}")
    print("=" * 70)

if __name__ == "__main__":
    get_product_ids_names()
