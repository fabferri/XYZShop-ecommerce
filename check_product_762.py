import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product

# Check if product 762 exists
try:
    product = Product.objects.get(id=762)
    print(f"Product 762 found: {product.name}")
    print(f"Slug: {product.slug}")
    print(f"Is online: {product.is_online}")
except Product.DoesNotExist:
    print("Product with ID 762 does not exist")
    
# Check if there's a product with the slug
products_with_slug = Product.objects.filter(slug='air-compressor-50l-25hp')
if products_with_slug.exists():
    print("\nProducts with slug 'air-compressor-50l-25hp':")
    for p in products_with_slug:
        print(f"  ID: {p.id}, Name: {p.name}, Is online: {p.is_online}")
else:
    print("\nNo product found with slug 'air-compressor-50l-25hp'")

# Search for similar product names
similar_products = Product.objects.filter(name__icontains='air compressor')
print(f"\nFound {similar_products.count()} products with 'air compressor' in name:")
for p in similar_products[:10]:
    print(f"  ID: {p.id}, Name: {p.name}, Slug: {p.slug}, Is online: {p.is_online}")
