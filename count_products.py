"""
Quick script to count products in database and exported file
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, Category
from exported_products import ALL_PRODUCTS

# Count in database
db_product_count = Product.objects.count()
db_category_count = Category.objects.count()

# Count in exported file
export_product_count = sum(len(products) for products in ALL_PRODUCTS.values())
export_category_count = len(ALL_PRODUCTS.keys())

print("=" * 60)
print("Product Count Comparison")
print("=" * 60)
print(f"\nCurrent Database:")
print(f"  Categories: {db_category_count}")
print(f"  Products: {db_product_count}")

print(f"\nExported File (exported_products.py):")
print(f"  Categories: {export_category_count}")
print(f"  Products: {export_product_count}")

print(f"\nDifference: {db_product_count - export_product_count} products")

if db_product_count > export_product_count:
    print(f"\n⚠️  WARNING: Database has {db_product_count - export_product_count} more products than the export!")
    print("   The restore script will NOT restore all products currently in the database.")
elif db_product_count == export_product_count:
    print("\n✅ Export file contains all products from database.")
else:
    print("\n✅ Export file is up to date.")

print("\n" + "=" * 60)
