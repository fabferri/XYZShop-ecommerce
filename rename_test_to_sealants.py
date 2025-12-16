import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, Category

def main():
    # Get or rename Test category
    try:
        test_category = Category.objects.get(slug='test')
        
        # Update to Sealants
        test_category.name = 'Sealants'
        test_category.slug = 'sealants'
        test_category.save()
        
        print(f"✅ Successfully renamed 'Test' category to 'Sealants'")
        
        # Count products in this category
        product_count = Product.objects.filter(category=test_category).count()
        print(f"   Category now has {product_count} products")
        
    except Category.DoesNotExist:
        # Create new Sealants category if Test doesn't exist
        sealants_category = Category.objects.create(
            name='Sealants',
            slug='sealants'
        )
        print(f" Created new 'Sealants' category")

if __name__ == '__main__':
    main()
