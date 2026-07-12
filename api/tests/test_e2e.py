"""
API End-to-End Tests
Full workflow tests covering register → token auth → browse products →
add to cart → create order → verify order, and other multi-step scenarios.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product


class TokenAuthEndToEndTest(TestCase):
    """Test complete flow: register -> get token -> use token for protected endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Drill', slug='drill',
            price=Decimal('89.99'), stock=10, available=True, is_online=True,
        )

    def test_register_then_use_token(self):
        reg = self.client.post('/api/auth/register/', {
            'username': 'apiuser',
            'email': 'api@example.com',
            'first_name': 'API',
            'last_name': 'User',
            'password': 'securepass123',
        })
        token = reg.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        profile = self.client.get('/api/auth/profile/')
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data['username'], 'apiuser')

    def test_login_then_create_order(self):
        User.objects.create_user(username='buyer', password='buyerpass123')
        login_resp = self.client.post('/api/auth/login/', {
            'username': 'buyer', 'password': 'buyerpass123',
        })
        token = login_resp.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        order_resp = self.client.post('/api/orders/create/', {
            'first_name': 'Buyer',
            'last_name': 'Test',
            'email': 'buyer@example.com',
            'address': '1 Market St',
            'postal_code': 'X1 1XX',
            'city': 'London',
        })
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)

    def test_login_then_write_review(self):
        User.objects.create_user(username='reviewer', password='reviewpass123')
        login_resp = self.client.post('/api/auth/login/', {
            'username': 'reviewer', 'password': 'reviewpass123',
        })
        token = login_resp.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        review_resp = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'comment': 'Excellent drill!'},
        )
        self.assertEqual(review_resp.status_code, status.HTTP_201_CREATED)


class FullCustomerJourneyTest(TestCase):
    """Register -> browse -> cart -> order -> verify -> review, end to end."""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Power Tools', slug='power-tools')
        self.drill = Product.objects.create(
            category=self.cat, name='Cordless Drill', slug='cordless-drill',
            description='18V cordless drill.', price=Decimal('89.99'),
            stock=10, available=True, is_online=True,
        )
        self.battery = Product.objects.create(
            category=self.cat, name='Spare Battery', slug='spare-battery',
            price=Decimal('24.50'), stock=30, available=True, is_online=True,
        )

    def test_complete_journey(self):
        # 1. Register and authenticate
        reg = self.client.post('/api/auth/register/', {
            'username': 'journey', 'email': 'journey@example.com',
            'first_name': 'Journey', 'last_name': 'Customer',
            'password': 'journeypass123',
        })
        self.assertEqual(reg.status_code, status.HTTP_201_CREATED)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reg.data['token']}")

        # 2. Browse categories and products
        cats = self.client.get('/api/categories/')
        self.assertEqual(cats.data['results'][0]['product_count'], 2)
        products = self.client.get('/api/products/?category__slug=power-tools')
        self.assertEqual(products.data['count'], 2)

        # 3. Add two products to the cart
        self.client.post('/api/cart/add/', {'product_id': self.drill.id, 'quantity': 1})
        self.client.post('/api/cart/add/', {'product_id': self.battery.id, 'quantity': 2})
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 3)
        self.assertEqual(Decimal(cart.data['total_price']), Decimal('138.99'))

        # 4. Create the order
        order = self.client.post('/api/orders/create/', {
            'first_name': 'Journey', 'last_name': 'Customer',
            'email': 'journey@example.com', 'address': '10 Test Rd',
            'postal_code': 'TE1 1ST', 'city': 'Testville',
        })
        self.assertEqual(order.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order.data['total_cost'], '138.99')
        order_id = order.data['id']

        # 5. Cart is cleared after ordering
        cart_after = self.client.get('/api/cart/')
        self.assertEqual(cart_after.data['total_items'], 0)

        # 6. Order appears in the user's order list and detail
        order_list = self.client.get('/api/orders/')
        self.assertEqual(order_list.data['count'], 1)
        detail = self.client.get(f'/api/orders/{order_id}/')
        self.assertEqual(len(detail.data['items']), 2)

        # 7. Leave a review on a purchased product
        review = self.client.post(
            f'/api/products/{self.drill.id}/reviews/create/',
            {'rating': 5, 'title': 'Love it', 'comment': 'Powerful and light.'},
        )
        self.assertEqual(review.status_code, status.HTTP_201_CREATED)
        detail = self.client.get(f'/api/products/{self.drill.id}/')
        self.assertEqual(detail.data['rating_count'], 1)
        self.assertEqual(detail.data['average_rating'], 5.0)

    def test_two_users_carts_are_isolated(self):
        u1 = APIClient()
        u2 = APIClient()
        User.objects.create_user(username='c1', password='pass12345')
        User.objects.create_user(username='c2', password='pass12345')
        t1 = u1.post('/api/auth/login/', {'username': 'c1', 'password': 'pass12345'}).data['token']
        t2 = u2.post('/api/auth/login/', {'username': 'c2', 'password': 'pass12345'}).data['token']
        u1.credentials(HTTP_AUTHORIZATION=f'Token {t1}')
        u2.credentials(HTTP_AUTHORIZATION=f'Token {t2}')
        u1.post('/api/cart/add/', {'product_id': self.drill.id, 'quantity': 2})
        # u2 cart should remain empty (separate sessions)
        self.assertEqual(u2.get('/api/cart/').data['total_items'], 0)
