"""
API Order Tests
Tests for order listing, detail retrieval, order creation from cart,
authentication requirements, and validation via /api/orders/ endpoints.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product
from orders.models import Order, OrderItem


class OrderListAPITest(TestCase):
    """Tests for GET /api/orders/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='buyer', password='pass123')
        self.other_user = User.objects.create_user(username='other', password='pass123')
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Drill', slug='drill',
            price=Decimal('89.99'), stock=10, available=True, is_online=True,
        )
        self.order = Order.objects.create(
            user=self.user, first_name='John', last_name='Doe',
            email='john@example.com', address='123 Main St',
            postal_code='AB1 2CD', city='London',
        )
        OrderItem.objects.create(
            order=self.order, product=self.product,
            price=Decimal('89.99'), quantity=1,
        )
        Order.objects.create(
            user=self.other_user, first_name='Jane', last_name='Smith',
            email='jane@example.com', address='456 Oak Ave',
            postal_code='EF3 4GH', city='Manchester',
        )

    def test_list_orders_unauthenticated(self):
        response = self.client.get('/api/orders/')
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])

    def test_list_orders_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_orders_only_own(self):
        """User should only see their own orders."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.order.id)

    def test_list_orders_has_expected_fields(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        order = response.data['results'][0]
        for field in [
            'id', 'first_name', 'last_name', 'email', 'status',
            'paid', 'payment_method', 'total_cost', 'item_count', 'created',
        ]:
            self.assertIn(field, order)

    def test_list_orders_total_cost(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.data['results'][0]['total_cost'], '89.99')

    def test_list_orders_item_count(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.data['results'][0]['item_count'], 1)


class OrderDetailAPITest(TestCase):
    """Tests for GET /api/orders/{id}/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='buyer', password='pass123')
        self.other_user = User.objects.create_user(username='other', password='pass123')
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Drill', slug='drill',
            price=Decimal('89.99'), stock=10, available=True, is_online=True,
        )
        self.order = Order.objects.create(
            user=self.user, first_name='John', last_name='Doe',
            email='john@example.com', address='123 Main St',
            postal_code='AB1 2CD', city='London',
        )
        OrderItem.objects.create(
            order=self.order, product=self.product,
            price=Decimal('89.99'), quantity=2,
        )

    def test_detail_status(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_has_all_fields(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/{self.order.id}/')
        for field in [
            'id', 'first_name', 'last_name', 'email', 'address',
            'postal_code', 'city', 'status', 'paid', 'payment_method',
            'payment_id', 'total_cost', 'items', 'created', 'updated',
        ]:
            self.assertIn(field, response.data)

    def test_detail_includes_items(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/{self.order.id}/')
        self.assertEqual(len(response.data['items']), 1)
        item = response.data['items'][0]
        self.assertEqual(item['product_name'], 'Drill')
        self.assertEqual(item['quantity'], 2)
        self.assertEqual(item['cost'], '179.98')

    def test_detail_total_cost(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.data['total_cost'], '179.98')

    def test_detail_unauthenticated(self):
        response = self.client.get(f'/api/orders/{self.order.id}/')
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])

    def test_detail_other_users_order(self):
        """Cannot view another user's order."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_nonexistent_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderCreateAPITest(TestCase):
    """Tests for POST /api/orders/create/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='buyer', password='pass123')
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Drill', slug='drill',
            price=Decimal('89.99'), stock=10, available=True, is_online=True,
        )
        self.order_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 Main St',
            'postal_code': 'AB1 2CD',
            'city': 'London',
        }

    def test_create_order_unauthenticated(self):
        response = self.client.post('/api/orders/create/', self.order_data)
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])

    def test_create_order_empty_cart(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/orders/create/', self.order_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_create_order_success(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 2})
        response = self.client.post('/api/orders/create/', self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_create_order_response_has_detail_format(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        response = self.client.post('/api/orders/create/', self.order_data)
        self.assertIn('items', response.data)
        self.assertIn('total_cost', response.data)
        self.assertEqual(response.data['first_name'], 'John')

    def test_create_order_clears_cart(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        self.client.post('/api/orders/create/', self.order_data)
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 0)

    def test_create_order_links_to_user(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        self.client.post('/api/orders/create/', self.order_data)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)

    def test_create_order_items_have_correct_price(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 3})
        self.client.post('/api/orders/create/', self.order_data)
        item = OrderItem.objects.first()
        self.assertEqual(item.price, Decimal('89.99'))
        self.assertEqual(item.quantity, 3)

    def test_create_order_multiple_products(self):
        p2 = Product.objects.create(
            category=self.cat, name='Saw', slug='saw',
            price=Decimal('29.99'), stock=5, available=True, is_online=True,
        )
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        self.client.post('/api/cart/add/', {'product_id': p2.id, 'quantity': 2})
        response = self.client.post('/api/orders/create/', self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderItem.objects.count(), 2)

    def test_create_order_missing_first_name(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        data = self.order_data.copy()
        del data['first_name']
        response = self.client.post('/api/orders/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_email(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        data = self.order_data.copy()
        del data['email']
        response = self.client.post('/api/orders/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_email(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        data = self.order_data.copy()
        data['email'] = 'not-an-email'
        response = self.client.post('/api/orders/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_address(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        data = self.order_data.copy()
        del data['address']
        response = self.client.post('/api/orders/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_city(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        data = self.order_data.copy()
        del data['city']
        response = self.client.post('/api/orders/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_defaults(self):
        """New order should default to unpaid / pending / card."""
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1})
        response = self.client.post('/api/orders/create/', self.order_data)
        self.assertFalse(response.data['paid'])
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['payment_method'], 'card')

    def test_create_order_total_cost_multiple_items(self):
        p2 = Product.objects.create(
            category=self.cat, name='Saw', slug='saw',
            price=Decimal('29.99'), stock=5, available=True, is_online=True,
        )
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 2})  # 179.98
        self.client.post('/api/cart/add/', {'product_id': p2.id, 'quantity': 1})            # 29.99
        response = self.client.post('/api/orders/create/', self.order_data)
        self.assertEqual(response.data['total_cost'], '209.97')

    def test_create_order_get_not_allowed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/create/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_order_decrements_stock(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 3})
        self.client.post('/api/orders/create/', self.order_data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)  # 10 - 3

    def test_create_order_decrements_stock_multiple_products(self):
        p2 = Product.objects.create(
            category=self.cat, name='Saw', slug='saw',
            price=Decimal('29.99'), stock=5, available=True, is_online=True,
        )
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 2})
        self.client.post('/api/cart/add/', {'product_id': p2.id, 'quantity': 4})
        self.client.post('/api/orders/create/', self.order_data)
        self.product.refresh_from_db()
        p2.refresh_from_db()
        self.assertEqual(self.product.stock, 8)  # 10 - 2
        self.assertEqual(p2.stock, 1)            # 5 - 4

    def test_create_order_insufficient_stock_rejected(self):
        low = Product.objects.create(
            category=self.cat, name='Rare Item', slug='rare-item',
            price=Decimal('5.00'), stock=1, available=True, is_online=True,
        )
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': low.id, 'quantity': 5})
        response = self.client.post('/api/orders/create/', self.order_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_create_order_insufficient_stock_no_order_created(self):
        low = Product.objects.create(
            category=self.cat, name='Rare Item', slug='rare-item',
            price=Decimal('5.00'), stock=1, available=True, is_online=True,
        )
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': low.id, 'quantity': 5})
        self.client.post('/api/orders/create/', self.order_data)
        # Transaction rolled back: no order, no order items, stock unchanged.
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        low.refresh_from_db()
        self.assertEqual(low.stock, 1)

    def test_create_order_insufficient_stock_keeps_cart(self):
        low = Product.objects.create(
            category=self.cat, name='Rare Item', slug='rare-item',
            price=Decimal('5.00'), stock=1, available=True, is_online=True,
        )
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': low.id, 'quantity': 5})
        self.client.post('/api/orders/create/', self.order_data)
        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['total_items'], 5)

    def test_create_order_exact_stock_succeeds(self):
        exact = Product.objects.create(
            category=self.cat, name='Exact Item', slug='exact-item',
            price=Decimal('5.00'), stock=3, available=True, is_online=True,
        )
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/cart/add/', {'product_id': exact.id, 'quantity': 3})
        response = self.client.post('/api/orders/create/', self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        exact.refresh_from_db()
        self.assertEqual(exact.stock, 0)


class OrderListOrderingAPITest(TestCase):
    """Ordering and isolation coverage for GET /api/orders/."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='buyer', password='pass123')
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.older = Order.objects.create(
            user=self.user, first_name='Old', last_name='Order',
            email='old@example.com', address='1 St', postal_code='A1', city='London',
        )
        self.newer = Order.objects.create(
            user=self.user, first_name='New', last_name='Order',
            email='new@example.com', address='2 St', postal_code='A2', city='London',
        )

    def test_orders_newest_first(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        # Meta ordering is ('-created',) -> newest order first
        self.assertEqual(response.data['results'][0]['id'], self.newer.id)

    def test_empty_order_list_for_new_user(self):
        fresh = User.objects.create_user(username='fresh', password='pass123')
        self.client.force_authenticate(user=fresh)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.data['count'], 0)

    def test_order_list_zero_total_no_items(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        result = next(o for o in response.data['results'] if o['id'] == self.older.id)
        self.assertEqual(result['total_cost'], '0')
        self.assertEqual(result['item_count'], 0)
