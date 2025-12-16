import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, Category

def demo_warehouse_functionality():
    """Demonstrate the warehouse functionality by creating test products"""
    print("Warehouse Management Demo")
    print("=" * 70)
    
    # Get or create a test category
    category, _ = Category.objects.get_or_create(
        slug='test-category',
        defaults={'name': 'Test Category'}
    )
    
    # Create 3 test products in warehouse (offline)
    test_products = [
        {
            'name': 'Test Product 1 - In Warehouse',
            'slug': 'test-product-1-warehouse',
            'price': 19.99,
            'stock': 50,
            'description': 'This product is in warehouse and NOT visible to customers',
            'available': True,
            'is_online': False  # In warehouse
        },
        {
            'name': 'Test Product 2 - Online',
            'slug': 'test-product-2-online',
            'price': 29.99,
            'stock': 30,
            'description': 'This product is ONLINE and visible to customers',
            'available': True,
            'is_online': True  # Online
        },
        {
            'name': 'Test Product 3 - In Warehouse',
            'slug': 'test-product-3-warehouse',
            'price': 39.99,
            'stock': 20,
            'description': 'This product is in warehouse awaiting approval',
            'available': True,
            'is_online': False  # In warehouse
        },
    ]
    
    created_products = []
    for product_data in test_products:
        product, created = Product.objects.get_or_create(
            slug=product_data['slug'],
            defaults={
                'category': category,
                'name': product_data['name'],
                'price': product_data['price'],
                'stock': product_data['stock'],
                'description': product_data['description'],
                'available': product_data['available'],
                'is_online': product_data['is_online']
            }
        )
        if created:
            created_products.append(product)
            status = "ONLINE (visible)" if product.is_online else "WAREHOUSE (hidden)"
            print(f"Created: {product.name}")
            print(f"  Status: {status}")
            print(f"  Price: £{product.price}")
            print()
    
    print("=" * 70)
    print("\nCurrent Status:")
    print(f"  - Total products in database: {Product.objects.count()}")
    print(f"  - Products ONLINE (visible to customers): {Product.objects.filter(is_online=True).count()}")
    print(f"  - Products in WAREHOUSE (not visible): {Product.objects.filter(is_online=False).count()}")
    
    print("\nHow to use:")
    print("  1. Visit http://127.0.0.1:8000/admin/products/product/")
    print("  2. Login with admin credentials (admin/admin123)")
    print("  3. You'll see the 'IS ONLINE' column with checkboxes")
    print("  4. Click the checkbox to toggle products online/offline")
    print("  5. Use 'Online' filter to see warehouse vs. online products")
    print("  6. Select multiple products and use bulk actions:")
    print("     - 'Move selected products ONLINE (visible to customers)'")
    print("     - 'Move selected products to WAREHOUSE (not visible)'")
    print("\nWarehouse functionality is ready to use!")

if __name__ == '__main__':
    demo_warehouse_functionality()
