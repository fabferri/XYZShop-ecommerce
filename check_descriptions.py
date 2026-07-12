"""
Check Product Descriptions
Displays how many products have descriptions and how many are missing them.
Shows the first 5 products without descriptions as a sample.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product

total = Product.objects.count()
without_desc = Product.objects.filter(description='').count()
with_desc = Product.objects.exclude(description='').count()

print(f'Total products: {total}')
print(f'With description: {with_desc}')
print(f'Without description: {without_desc}')

# Show sample of products without descriptions
if without_desc > 0:
    print('\nFirst 5 products without descriptions:')
    for p in Product.objects.filter(description='')[:5]:
        print(f'  - {p.name}')
