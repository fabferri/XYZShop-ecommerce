import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product

# Find products with reviews
products_with_reviews = Product.objects.filter(reviews__isnull=False).distinct()

print('Products with reviews (you can visit these URLs):\n')
print('='*80)

for product in products_with_reviews:
    url = f'http://127.0.0.1:8000/{product.id}/{product.slug}/'
    avg_rating = product.get_average_rating()
    count = product.get_rating_count()
    stars = '★' * int(avg_rating) + '☆' * (5 - int(avg_rating))
    
    print(f'\n{product.name}')
    print(f'  Rating: {stars} ({avg_rating}/5 - {count} review{"s" if count != 1 else ""})')
    print(f'  URL: {url}')

print('\n' + '='*80)
print('\nVisit any of these URLs to see customer reviews and star ratings!')
print('Each product page will show:')
print('  ✓ Average rating with stars')
print('  ✓ Total number of reviews')
print('  ✓ Rating distribution (5-star breakdown)')
print('  ✓ Individual customer reviews with:')
print('    - Star rating')
print('    - Review title')
print('    - Review comment')
print('    - Customer name')
print('    - Review date')
print('    - Verified purchase badge (if applicable)')
