"""
Delete All Records Script
This script deletes all records from the XYZShop database.
WARNING: This will permanently delete all data!
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, Category, Sale, ProductReview, ProductPriceHistory
from orders.models import Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()

def delete_all_records():
    """Delete all records from the database"""
    print("=" * 60)
    print("WARNING: This will delete ALL data from the database!")
    print("=" * 60)
    
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    print("\nDeleting records...")
    
    # Delete in order to respect foreign key constraints
    
    # Delete Sales
    sale_count = Sale.objects.count()
    Sale.objects.all().delete()
    print(f"Deleted {sale_count} sales")
    
    # Delete Order Items
    order_item_count = OrderItem.objects.count()
    OrderItem.objects.all().delete()
    print(f"Deleted {order_item_count} order items")
    
    # Delete Orders
    order_count = Order.objects.count()
    Order.objects.all().delete()
    print(f"Deleted {order_count} orders")
    
    # Delete Product Reviews
    review_count = ProductReview.objects.count()
    ProductReview.objects.all().delete()
    print(f"Deleted {review_count} product reviews")
    
    # Delete Product Price History
    price_history_count = ProductPriceHistory.objects.count()
    ProductPriceHistory.objects.all().delete()
    print(f"Deleted {price_history_count} price history records")
    
    # Delete Products
    product_count = Product.objects.count()
    Product.objects.all().delete()
    print(f"Deleted {product_count} products")
    
    # Delete Categories
    category_count = Category.objects.count()
    Category.objects.all().delete()
    print(f"Deleted {category_count} categories")
    
    # Delete all Users (including superusers)
    user_count = User.objects.count()
    User.objects.all().delete()
    print(f"Deleted {user_count} users (including superusers)")
    
    print("\n" + "=" * 60)
    print("SUCCESS: All records deleted from database")
    print("ALL data has been removed, including superuser accounts")
    print("=" * 60)

if __name__ == '__main__':
    delete_all_records()
