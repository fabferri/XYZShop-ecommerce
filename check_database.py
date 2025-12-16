"""
Check Database Status
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, Category

print("=" * 60)
print("Database Status")
print("=" * 60)
print(f"\nTotal products: {Product.objects.count()}")
print(f"Total categories: {Category.objects.count()}")
print(f"Products online: {Product.objects.filter(is_online=True).count()}")
print(f"Products in warehouse: {Product.objects.filter(is_online=False).count()}")

print("\nProducts by category:")
for cat in Category.objects.all():
    total = Product.objects.filter(category=cat).count()
    online = Product.objects.filter(category=cat, is_online=True).count()
    warehouse = Product.objects.filter(category=cat, is_online=False).count()
    print(f"  {cat.name}: {total} total ({online} online, {warehouse} warehouse)")

print("=" * 60)
