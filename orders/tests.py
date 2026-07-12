"""
Orders Tests
Tests for order creation, payment flow, and order management.
"""
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Category, Product
from orders.models import Order, OrderItem


class OrderCreateViewTest(TestCase):
    """Tests for the template-based checkout (orders:order_create)."""

    def setUp(self):
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Drill', slug='drill',
            price=Decimal('89.99'), stock=10, available=True, is_online=True,
        )
        self.order_data = {
            'first_name': 'John', 'last_name': 'Doe',
            'email': 'john@example.com', 'address': '123 Main St',
            'postal_code': 'AB1 2CD', 'city': 'London',
        }

    def _add_to_cart(self, product, quantity):
        self.client.post(
            reverse('cart:cart_add', args=[product.id]),
            {'quantity': quantity, 'update': False},
        )

    def test_order_create_decrements_stock(self):
        self._add_to_cart(self.product, 3)
        self.client.post(reverse('orders:order_create'), self.order_data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_order_create_links_authenticated_user(self):
        user = User.objects.create_user(username='buyer', password='pass12345')
        self.client.login(username='buyer', password='pass12345')
        self._add_to_cart(self.product, 1)
        self.client.post(reverse('orders:order_create'), self.order_data)
        order = Order.objects.first()
        self.assertEqual(order.user, user)

    def test_order_create_insufficient_stock_no_order(self):
        low = Product.objects.create(
            category=self.cat, name='Rare', slug='rare',
            price=Decimal('5.00'), stock=1, available=True, is_online=True,
        )
        self._add_to_cart(low, 5)
        response = self.client.post(reverse('orders:order_create'), self.order_data, follow=True)
        self.assertEqual(Order.objects.count(), 0)
        low.refresh_from_db()
        self.assertEqual(low.stock, 1)
        # User is redirected back to the cart.
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_order_create_exact_stock_succeeds(self):
        exact = Product.objects.create(
            category=self.cat, name='Exact', slug='exact',
            price=Decimal('5.00'), stock=2, available=True, is_online=True,
        )
        self._add_to_cart(exact, 2)
        self.client.post(reverse('orders:order_create'), self.order_data)
        exact.refresh_from_db()
        self.assertEqual(exact.stock, 0)
        self.assertEqual(Order.objects.count(), 1)


class PaymentViewTest(TestCase):
    """Tests for the payment simulation flow (orders:payment)."""

    def setUp(self):
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Drill', slug='drill',
            price=Decimal('89.99'), stock=10, available=True, is_online=True,
        )
        self.order = Order.objects.create(
            first_name='John', last_name='Doe', email='john@example.com',
            address='123 Main St', postal_code='AB1 2CD', city='London',
        )
        OrderItem.objects.create(
            order=self.order, product=self.product,
            price=Decimal('89.99'), quantity=1,
        )

    def test_payment_marks_order_paid(self):
        self.client.post(
            reverse('orders:payment', args=[self.order.id]),
            {'payment_method': 'paypal'},
        )
        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)
        self.assertEqual(self.order.status, 'processing')
        self.assertEqual(self.order.payment_method, 'paypal')
        self.assertTrue(self.order.payment_id)

    def test_payment_done_requires_paid_order(self):
        response = self.client.get(reverse('orders:payment_done', args=[self.order.id]))
        self.assertEqual(response.status_code, 404)

