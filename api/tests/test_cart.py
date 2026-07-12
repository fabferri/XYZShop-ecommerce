"""
API Cart Tests
Tests for session-based cart operations: view cart, add/remove items,
clear cart, quantity validation, and cart totals via /api/cart/ endpoints.
"""
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product


class CartDetailAPITest(TestCase):
    """Tests for GET /api/cart/"""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Wrench', slug='wrench',
            price=Decimal('14.99'), stock=20, available=True, is_online=True,
        )

    def test_empty_cart(self):
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 0)
        self.assertEqual(response.data['items'], [])
        self.assertEqual(Decimal(response.data['total_price']), Decimal('0'))

    def test_cart_has_expected_fields(self):
        response = self.client.get('/api/cart/')
        for field in ['items', 'total_items', 'total_price']:
            self.assertIn(field, response.data)

    def test_cart_after_adding_item(self):
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 2})
        response = self.client.get('/api/cart/')
        self.assertEqual(response.data['total_items'], 2)
        self.assertEqual(len(response.data['items']), 1)
        item = response.data['items'][0]
        self.assertEqual(item['product_id'], self.product.id)
        self.assertEqual(item['product_name'], 'Wrench')
        self.assertEqual(Decimal(item['price']), Decimal('14.99'))
        self.assertEqual(item['quantity'], 2)
        self.assertEqual(Decimal(item['total_price']), Decimal('29.98'))

    def test_cart_total_price_multiple_items(self):
        p2 = Product.objects.create(
            category=self.cat, name='Pliers', slug='pliers',
            price=Decimal('10.00'), stock=10, available=True, is_online=True,
        )
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        self.client.post('/api/cart/add/', {'product_id': p2.id, 'quantity': 3})
        response = self.client.get('/api/cart/')
        self.assertEqual(response.data['total_items'], 4)
        self.assertEqual(Decimal(response.data['total_price']), Decimal('44.99'))


class CartAddAPITest(TestCase):
    """Tests for POST /api/cart/add/"""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Wrench', slug='wrench',
            price=Decimal('14.99'), stock=20, available=True, is_online=True,
        )

    def test_add_to_cart(self):
        response = self.client.post(
            '/api/cart/add/',
            {'product_id': self.product.id, 'quantity': 2},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_default_quantity_is_one(self):
        self.client.post('/api/cart/add/', {'product_id': self.product.id})
        response = self.client.get('/api/cart/')
        self.assertEqual(response.data['total_items'], 1)

    def test_add_accumulates_quantity(self):
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 2})
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 3})
        response = self.client.get('/api/cart/')
        self.assertEqual(response.data['total_items'], 5)

    def test_add_update_quantity_replaces(self):
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 5})
        self.client.post('/api/cart/add/', {
            'product_id': self.product.id,
            'quantity': 2,
            'update_quantity': True,
        })
        response = self.client.get('/api/cart/')
        self.assertEqual(response.data['total_items'], 2)

    def test_add_nonexistent_product(self):
        response = self.client.post('/api/cart/add/', {'product_id': 99999, 'quantity': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_offline_product(self):
        self.product.is_online = False
        self.product.save()
        response = self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_unavailable_product(self):
        self.product.available = False
        self.product.save()
        response = self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_missing_product_id(self):
        response = self.client.post('/api/cart/add/', {'quantity': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_quantity_zero(self):
        response = self.client.post(
            '/api/cart/add/',
            {'product_id': self.product.id, 'quantity': 0},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_quantity_exceeds_max(self):
        response = self.client.post(
            '/api/cart/add/',
            {'product_id': self.product.id, 'quantity': 21},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_negative_quantity(self):
        response = self.client.post(
            '/api/cart/add/',
            {'product_id': self.product.id, 'quantity': -1},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_get_method_not_allowed(self):
        response = self.client.get('/api/cart/add/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CartRemoveAPITest(TestCase):
    """Tests for POST /api/cart/remove/{product_id}/"""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Wrench', slug='wrench',
            price=Decimal('14.99'), stock=20, available=True, is_online=True,
        )

    def test_remove_from_cart(self):
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        response = self.client.post(f'/api/cart/remove/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 0)

    def test_remove_nonexistent_product(self):
        response = self.client.post('/api/cart/remove/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_product_not_in_cart(self):
        """Removing a valid product that isn't in cart should succeed silently."""
        response = self.client.post(f'/api/cart/remove/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_get_method_not_allowed(self):
        response = self.client.get(f'/api/cart/remove/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CartClearAPITest(TestCase):
    """Tests for POST /api/cart/clear/"""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Wrench', slug='wrench',
            price=Decimal('14.99'), stock=20, available=True, is_online=True,
        )

    def test_clear_cart_with_items(self):
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 3})
        response = self.client.post('/api/cart/clear/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 0)

    def test_clear_empty_cart(self):
        response = self.client.post('/api/cart/clear/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_clear_get_method_not_allowed(self):
        response = self.client.get('/api/cart/clear/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CartBoundaryAPITest(TestCase):
    """Boundary and edge-case coverage for the cart endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Wrench', slug='wrench',
            price=Decimal('14.99'), stock=20, available=True, is_online=True,
        )

    def test_add_quantity_min_boundary_one(self):
        response = self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_quantity_max_boundary_twenty(self):
        response = self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 20})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 20)

    def test_cart_persists_across_requests(self):
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 2})
        # Second GET on the same client/session should still see the item
        self.client.get('/api/cart/')
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 2)

    def test_cart_price_frozen_at_add_time(self):
        """Cart keeps the price captured when the item was added."""
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        self.product.price = Decimal('99.99')
        self.product.save()
        cart = self.client.get('/api/cart/')
        self.assertEqual(Decimal(cart.data['items'][0]['price']), Decimal('14.99'))

    def test_remove_one_keeps_others(self):
        p2 = Product.objects.create(
            category=self.cat, name='Pliers', slug='pliers',
            price=Decimal('10.00'), stock=10, available=True, is_online=True,
        )
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        self.client.post('/api/cart/add/', {'product_id': p2.id, 'quantity': 1})
        self.client.post(f'/api/cart/remove/{self.product.id}/')
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 1)
        self.assertEqual(cart.data['items'][0]['product_id'], p2.id)

    def test_update_quantity_false_accumulates(self):
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 2})
        self.client.post('/api/cart/add/', {
            'product_id': self.product.id, 'quantity': 3, 'update_quantity': False,
        })
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 5)

    def test_add_string_quantity_coerced(self):
        response = self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': '4'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 4)

    def test_add_non_integer_quantity_rejected(self):
        response = self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 'abc'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
