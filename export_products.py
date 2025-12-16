"""
Export All Product Definitions from Database
This script exports all existing products to a Python file format
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, Category

def export_products():
    """Export all products to a formatted Python file"""
    
    output_file = 'exported_products.py'
    
    print("=" * 60)
    print("Exporting Product Definitions from Database")
    print("=" * 60)
    
    categories = Category.objects.all().order_by('name')
    total_products = Product.objects.count()
    
    print(f"\nFound {total_products} products in {categories.count()} categories")
    print(f"Exporting to: {output_file}\n")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""\n')
        f.write('Exported Product Definitions\n')
        f.write(f'Total Products: {total_products}\n')
        f.write(f'Total Categories: {categories.count()}\n')
        f.write('"""\n\n')
        
        f.write('# Category and Product Data\n\n')
        
        # Export categories
        f.write('CATEGORIES = [\n')
        for cat in categories:
            f.write(f"    {{'name': '{cat.name}', 'slug': '{cat.slug}'}},\n")
        f.write(']\n\n')
        
        # Export products by category
        for category in categories:
            products = Product.objects.filter(category=category).order_by('name')
            
            if products.count() == 0:
                continue
                
            f.write(f'# {category.name} - {products.count()} products\n')
            f.write(f'{category.slug.upper().replace("-", "_")}_PRODUCTS = [\n')
            
            for product in products:
                f.write('    {\n')
                f.write(f"        'name': '{product.name}',\n")
                f.write(f"        'slug': '{product.slug}',\n")
                
                # Escape description
                desc = product.description.replace("'", "\\'").replace('\n', ' ')
                f.write(f"        'description': '{desc}',\n")
                
                f.write(f"        'price': {product.price},\n")
                f.write(f"        'cost_price': {product.cost_price},\n")
                f.write(f"        'stock': {product.stock},\n")
                f.write(f"        'available': {product.available},\n")
                f.write(f"        'is_online': {product.is_online},\n")
                
                # Extract just the filename from image path
                if product.image:
                    image_name = os.path.basename(str(product.image))
                    f.write(f"        'image': '{image_name}',\n")
                else:
                    f.write(f"        'image': '',\n")
                    
                f.write('    },\n')
            
            f.write(']\n\n')
            
            print(f"  {category.name}: {products.count()} products exported")
        
        # Create summary
        f.write('# Summary by Category\n')
        f.write('ALL_PRODUCTS = {\n')
        for category in categories:
            products_count = Product.objects.filter(category=category).count()
            if products_count > 0:
                var_name = category.slug.upper().replace('-', '_') + '_PRODUCTS'
                f.write(f"    '{category.slug}': {var_name},\n")
        f.write('}\n')
    
    print("\n" + "=" * 60)
    print(f"SUCCESS: Exported {total_products} products to {output_file}")
    print("=" * 60)

if __name__ == '__main__':
    export_products()
