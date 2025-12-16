import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product

def set_cost_prices():
    """Set realistic cost prices for all products (60-70% of selling price for typical retail margin)"""
    print(" Setting cost prices for all products...")
    print("=" * 60)
    
    products = Product.objects.all()
    count = 0
    
    for product in products:
        # Set cost price to approximately 65% of selling price (giving ~54% margin)
        # This is typical for retail hardware/tools
        cost_percentage = Decimal('0.65')
        product.cost_price = (product.price * cost_percentage).quantize(Decimal('0.01'))
        product.save()
        
        margin = product.get_margin_percentage()
        count += 1
        
        if count <= 10:  # Show first 10 as examples
            print(f" {product.name[:50]}")
            print(f"  Cost: £{product.cost_price} | Sell: £{product.price} | Margin: {margin}%")
    
    print("=" * 60)
    print(f" SUCCESS: Set cost prices for {count} products!")
    print(f" Average margin: ~54% (cost = 65% of selling price)")
    print(f" Administrators can now edit cost prices in admin panel")
    print(f"   to see actual profit margins for each product")

if __name__ == '__main__':
    set_cost_prices()
