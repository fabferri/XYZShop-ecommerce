import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, ProductReview
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a sample user if not exists
user, created = User.objects.get_or_create(
    username='customer1',
    defaults={
        'email': 'customer1@example.com',
        'first_name': 'John',
        'last_name': 'Smith'
    }
)
if created:
    user.set_password('password123')
    user.save()
    print(f'Created user: {user.username}')
else:
    print(f'Using existing user: {user.username}')

# Get some products to review
products = Product.objects.all()[:10]

reviews_data = [
    {
        'rating': 5,
        'title': 'Excellent quality',
        'comment': 'This product exceeded my expectations. Very durable and works perfectly. Highly recommended for professional use.',
    },
    {
        'rating': 4,
        'title': 'Good value for money',
        'comment': 'Solid product that does the job well. Easy to use and good build quality. Would buy again.',
    },
    {
        'rating': 5,
        'title': 'Perfect for DIY projects',
        'comment': 'Exactly what I needed for my home renovation project. Great performance and very reliable.',
    },
    {
        'rating': 3,
        'title': 'Decent product',
        'comment': 'Does what it says on the tin. Nothing special but gets the job done. Fair price.',
    },
    {
        'rating': 5,
        'title': 'Outstanding!',
        'comment': 'Best purchase I\'ve made this year. Quality construction, easy to install, and performs flawlessly.',
    },
    {
        'rating': 4,
        'title': 'Very satisfied',
        'comment': 'Great product for both professional and DIY use. Good quality materials and finish.',
    },
    {
        'rating': 5,
        'title': 'Highly recommend',
        'comment': 'Professional quality at a reasonable price. Would definitely recommend to friends and colleagues.',
    },
    {
        'rating': 4,
        'title': 'Good purchase',
        'comment': 'Happy with this purchase. Works as expected and seems well made. Good customer service too.',
    },
    {
        'rating': 5,
        'title': 'Fantastic product',
        'comment': 'Couldn\'t be happier with this. Excellent quality and performance. Well worth the money.',
    },
    {
        'rating': 4,
        'title': 'Reliable and sturdy',
        'comment': 'Solid construction and reliable performance. A bit pricey but quality justifies the cost.',
    },
]

print(f'\nCreating sample reviews for {len(products)} products...\n')

for idx, product in enumerate(products):
    review_data = reviews_data[idx]
    
    # Check if review already exists
    existing = ProductReview.objects.filter(product=product, user=user).exists()
    
    if not existing:
        review = ProductReview.objects.create(
            product=product,
            user=user,
            rating=review_data['rating'],
            title=review_data['title'],
            comment=review_data['comment'],
            verified_purchase=True  # Mark as verified purchase
        )
        stars = '★' * review.rating + '☆' * (5 - review.rating)
        print(f'✓ Created review for: {product.name}')
        print(f'  {stars} ({review.rating}/5) - {review.title}')
    else:
        print(f'- Skipped: {product.name} (already has review from this user)')

print('\n' + '='*80)
print('Sample reviews created successfully!')
print('\nYou can now:')
print('1. View reviews in the Django admin panel')
print('2. See average ratings on products')
print('3. Manage reviews through the ProductReview admin')
