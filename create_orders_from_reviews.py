import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import ProductReview
from orders.models import Order, OrderItem

print('Creating orders for all reviewed products...\n')
print('='*80)

# Get all reviews
reviews = ProductReview.objects.select_related('user', 'product').all()

print(f'Found {reviews.count()} reviews to process\n')

# Addresses for fake orders
addresses = [
    {'address': '123 High Street', 'city': 'London', 'postal_code': 'SW1A 1AA'},
    {'address': '45 Queen Road', 'city': 'Manchester', 'postal_code': 'M1 1AA'},
    {'address': '78 King Avenue', 'city': 'Birmingham', 'postal_code': 'B1 1AA'},
    {'address': '12 Church Lane', 'city': 'Leeds', 'postal_code': 'LS1 1AA'},
    {'address': '56 Park Street', 'city': 'Bristol', 'postal_code': 'BS1 1AA'},
    {'address': '34 Station Road', 'city': 'Liverpool', 'postal_code': 'L1 1AA'},
    {'address': '89 Market Place', 'city': 'Newcastle', 'postal_code': 'NE1 1AA'},
    {'address': '67 Victoria Drive', 'city': 'Edinburgh', 'postal_code': 'EH1 1AA'},
    {'address': '23 Mill Street', 'city': 'Cardiff', 'postal_code': 'CF1 1AA'},
    {'address': '91 Bridge Road', 'city': 'Glasgow', 'postal_code': 'G1 1AA'},
]

payment_methods = ['card', 'paypal', 'bank', 'cash']
statuses = ['delivered', 'delivered', 'delivered', 'shipped']  # Mostly delivered

# Group reviews by user
user_reviews = {}
for review in reviews:
    if review.user not in user_reviews:
        user_reviews[review.user] = []
    user_reviews[review.user].append(review)

created_orders = 0
created_items = 0

for user, user_review_list in user_reviews.items():
    # Decide: create one order with all items or separate orders
    # Let's create 1-3 orders per user with random grouping
    num_orders = min(random.randint(1, 3), len(user_review_list))
    
    # Shuffle reviews and split into groups
    random.shuffle(user_review_list)
    reviews_per_order = len(user_review_list) // num_orders
    
    for order_idx in range(num_orders):
        # Get reviews for this order
        start_idx = order_idx * reviews_per_order
        if order_idx == num_orders - 1:
            # Last order gets remaining reviews
            order_reviews = user_review_list[start_idx:]
        else:
            order_reviews = user_review_list[start_idx:start_idx + reviews_per_order]
        
        if not order_reviews:
            continue
        
        # Select address
        address_data = random.choice(addresses)
        
        # Create order date (before the review dates)
        oldest_review = min(order_reviews, key=lambda r: r.created)
        days_before = random.randint(7, 30)  # Order placed 7-30 days before first review
        order_date = oldest_review.created - timedelta(days=days_before)
        
        # Create order
        order = Order.objects.create(
            user=user,
            first_name=user.first_name or user.username,
            last_name=user.last_name or 'User',
            email=user.email or f'{user.username}@email.com',
            address=address_data['address'],
            postal_code=address_data['postal_code'],
            city=address_data['city'],
            paid=True,
            payment_method=random.choice(payment_methods),
            payment_id=f'PAY-{random.randint(100000, 999999)}',
            status=random.choice(statuses)
        )
        
        # Set the created date manually
        order.created = order_date
        order.save(update_fields=['created'])
        
        created_orders += 1
        
        # Create order items
        total_items = 0
        for review in order_reviews:
            quantity = random.randint(1, 3)
            
            OrderItem.objects.create(
                order=order,
                product=review.product,
                price=review.product.price,
                quantity=quantity
            )
            total_items += quantity
            created_items += 1
        
        print(f'✓ Order #{order.id} for {user.get_full_name() or user.username}')
        print(f'  - {len(order_reviews)} products, {total_items} items total')
        print(f'  - Total: £{order.get_total_cost():.2f}')
        print(f'  - Status: {order.get_status_display()}')
        print(f'  - Date: {order.created.strftime("%Y-%m-%d")}')
        print()

print('='*80)
print(f'\nCompleted!')
print(f'  Orders created: {created_orders}')
print(f'  Order items created: {created_items}')
print(f'\nTotal in database:')
print(f'  Total orders: {Order.objects.count()}')
print(f'  Total order items: {OrderItem.objects.count()}')
print(f'  Users with orders: {Order.objects.values("user").distinct().count()}')
