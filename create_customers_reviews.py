import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, ProductReview
from django.contrib.auth import get_user_model

User = get_user_model()

# Customer data
customers = [
    {'username': 'sarah_jones', 'first_name': 'Sarah', 'last_name': 'Jones', 'email': 'sarah.jones@email.com'},
    {'username': 'mike_brown', 'first_name': 'Mike', 'last_name': 'Brown', 'email': 'mike.brown@email.com'},
    {'username': 'emma_wilson', 'first_name': 'Emma', 'last_name': 'Wilson', 'email': 'emma.wilson@email.com'},
    {'username': 'james_taylor', 'first_name': 'James', 'last_name': 'Taylor', 'email': 'james.taylor@email.com'},
    {'username': 'olivia_davis', 'first_name': 'Olivia', 'last_name': 'Davis', 'email': 'olivia.davis@email.com'},
    {'username': 'david_miller', 'first_name': 'David', 'last_name': 'Miller', 'email': 'david.miller@email.com'},
    {'username': 'sophie_anderson', 'first_name': 'Sophie', 'last_name': 'Anderson', 'email': 'sophie.anderson@email.com'},
    {'username': 'ryan_thomas', 'first_name': 'Ryan', 'last_name': 'Thomas', 'email': 'ryan.thomas@email.com'},
    {'username': 'lucy_jackson', 'first_name': 'Lucy', 'last_name': 'Jackson', 'email': 'lucy.jackson@email.com'},
    {'username': 'adam_white', 'first_name': 'Adam', 'last_name': 'White', 'email': 'adam.white@email.com'},
]

# Positive reviews (4-5 stars)
positive_reviews = [
    {'rating': 5, 'title': 'Excellent product!', 'comment': 'This exceeded all my expectations. Quality is outstanding and works perfectly. Highly recommend!'},
    {'rating': 5, 'title': 'Perfect for the job', 'comment': 'Exactly what I needed. Great quality and very durable. Will definitely buy again.'},
    {'rating': 5, 'title': 'Best purchase ever', 'comment': 'Cannot fault this product at all. Professional quality at a great price. Five stars!'},
    {'rating': 4, 'title': 'Very good quality', 'comment': 'Really pleased with this purchase. Does exactly what it says and feels well made.'},
    {'rating': 4, 'title': 'Great value', 'comment': 'Good product for the money. Works well and seems durable. Happy with my purchase.'},
    {'rating': 5, 'title': 'Highly recommended', 'comment': 'Brilliant product! Easy to use and excellent quality. Would recommend to anyone.'},
    {'rating': 4, 'title': 'Solid product', 'comment': 'Very satisfied with this. Good build quality and does the job well.'},
    {'rating': 5, 'title': 'Outstanding quality', 'comment': 'Top-notch product! Better than expected. Professional grade and worth every penny.'},
    {'rating': 4, 'title': 'Good buy', 'comment': 'Happy with this purchase. Works as described and seems to be good quality.'},
    {'rating': 5, 'title': 'Fantastic!', 'comment': 'Absolutely love this product. Works brilliantly and feels very sturdy. Excellent!'},
]

# Mixed/neutral reviews (3 stars)
neutral_reviews = [
    {'rating': 3, 'title': 'Does the job', 'comment': 'It\'s okay. Nothing special but works as expected. Fair price for what you get.'},
    {'rating': 3, 'title': 'Average product', 'comment': 'Not bad, not great. Does what it needs to do. Could be better quality for the price.'},
    {'rating': 3, 'title': 'Acceptable', 'comment': 'Decent product overall. A few minor issues but generally works fine.'},
    {'rating': 3, 'title': 'It\'s alright', 'comment': 'Middle of the road. Works but nothing to write home about. Adequate for basic use.'},
    {'rating': 3, 'title': 'Reasonable', 'comment': 'Fair product. Gets the job done but I expected slightly better quality.'},
]

# Negative reviews (1-2 stars)
negative_reviews = [
    {'rating': 2, 'title': 'Disappointing', 'comment': 'Not great quality. Works but feels cheap and flimsy. Expected better for the price.'},
    {'rating': 1, 'title': 'Poor quality', 'comment': 'Really disappointed with this. Broke after minimal use. Would not recommend at all.'},
    {'rating': 2, 'title': 'Not impressed', 'comment': 'Below average product. Doesn\'t feel durable and had issues from the start.'},
    {'rating': 1, 'title': 'Waste of money', 'comment': 'Terrible quality. Stopped working after a week. Save your money and buy something better.'},
    {'rating': 2, 'title': 'Could be better', 'comment': 'Not very happy with this purchase. Quality is questionable and doesn\'t work as well as expected.'},
]

print('Creating customers and reviews...\n')
print('='*80)

# Get all products
all_products = list(Product.objects.all())

if len(all_products) < 100:
    print(f'Warning: Only {len(all_products)} products available')

created_users = 0
created_reviews = 0

for customer_data in customers:
    # Create or get user
    user, created = User.objects.get_or_create(
        username=customer_data['username'],
        defaults={
            'email': customer_data['email'],
            'first_name': customer_data['first_name'],
            'last_name': customer_data['last_name']
        }
    )
    
    if created:
        user.set_password('password123')
        user.save()
        created_users += 1
        print(f'\n✓ Created customer: {user.get_full_name()} ({user.username})')
    else:
        print(f'\n- Using existing customer: {user.get_full_name()} ({user.username})')
    
    # Select 10 random products for this customer
    customer_products = random.sample(all_products, min(10, len(all_products)))
    
    # Create reviews with mixed ratings
    for idx, product in enumerate(customer_products):
        # Check if review already exists
        if ProductReview.objects.filter(product=product, user=user).exists():
            print(f'  - Skipped: {product.name} (already reviewed)')
            continue
        
        # Determine review type: 60% positive, 20% neutral, 20% negative
        rand = random.random()
        if rand < 0.6:
            review_data = random.choice(positive_reviews)
        elif rand < 0.8:
            review_data = random.choice(neutral_reviews)
        else:
            review_data = random.choice(negative_reviews)
        
        # Create review
        review = ProductReview.objects.create(
            product=product,
            user=user,
            rating=review_data['rating'],
            title=review_data['title'],
            comment=review_data['comment'],
            verified_purchase=True
        )
        
        stars = '★' * review.rating + '☆' * (5 - review.rating)
        created_reviews += 1
        print(f'  ✓ {stars} {product.name[:50]}')

print('\n' + '='*80)
print(f'\nCompleted!')
print(f'  New customers created: {created_users}')
print(f'  New reviews created: {created_reviews}')
print(f'\nTotal in database:')
print(f'  Users: {User.objects.count()}')
print(f'  Reviews: {ProductReview.objects.count()}')
print(f'  Products with reviews: {Product.objects.filter(reviews__isnull=False).distinct().count()}')
