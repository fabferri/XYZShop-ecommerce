import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, ProductReview

print('Product Rating System Summary')
print('='*80)

# Get products with reviews
products_with_reviews = Product.objects.filter(reviews__isnull=False).distinct()

print(f'\nTotal products: {Product.objects.count()}')
print(f'Products with reviews: {products_with_reviews.count()}')
print(f'Total reviews: {ProductReview.objects.count()}')

print('\n' + '-'*80)
print('Sample products with ratings:\n')

for product in products_with_reviews[:5]:
    avg_rating = product.get_average_rating()
    count = product.get_rating_count()
    stars = '★' * int(avg_rating) + '☆' * (5 - int(avg_rating))
    
    print(f'{product.name}')
    print(f'  {stars} {avg_rating}/5.0 ({count} review{"s" if count != 1 else ""})')
    print()

print('-'*80)
print('\nFeatures implemented:')
print('✓ ProductReview model with 1-5 star ratings')
print('✓ Customer comments/reviews')
print('✓ Unique constraint (one review per user per product)')
print('✓ Verified purchase flag')
print('✓ Average rating calculation')
print('✓ Rating distribution (5-star breakdown)')
print('✓ Admin interface with visual star display')
print('✓ Reviews displayed on product detail page')
print('✓ Rating summary with statistics')
print('\nAccess the admin panel to:')
print('- View all reviews: /admin/products/productreview/')
print('- Manage product reviews within product detail pages')
print('- Delete inappropriate reviews')
print('- See visual star ratings')
