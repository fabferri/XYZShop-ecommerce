import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product

# Set product 762 online
try:
    product = Product.objects.get(id=762)
    product.is_online = True
    product.save()
    print(f"Successfully set product '{product.name}' (ID: {product.id}) online")
    print(f"URL: http://127.0.0.1:8000/{product.id}/{product.slug}/")
except Product.DoesNotExist:
    print("Product with ID 762 does not exist")
