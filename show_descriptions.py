import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()


from products.models import Product

numrecords = Product.objects.count()
print(f'Total number of products: {numrecords}\n')

# Show sample of updated descriptions
print('Sample of updated product descriptions:\n')
print('='*80)

products = Product.objects.all()[:numrecords]
for p in products:
    print(f'\nProduct: {p.name}')
    print(f'Category: {p.category.name}')
    print(f'Description: {p.description}')
    print('-'*80)
