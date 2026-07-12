"""
API Category Tests
Tests for category listing, product counts, and filtering
via /api/categories/ endpoint.
"""
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product


class CategoryListAPITest(TestCase):
    """Tests for GET /api/categories/"""

    def setUp(self):
        self.client = APIClient()
        self.cat1 = Category.objects.create(name='Hand Tools', slug='hand-tools')
        self.cat2 = Category.objects.create(name='Power Tools', slug='power-tools')
        self.cat_empty = Category.objects.create(name='Gardening', slug='gardening')
        Product.objects.create(
            category=self.cat1, name='Hammer', slug='hammer',
            price=Decimal('19.99'), stock=10, available=True, is_online=True,
        )
        Product.objects.create(
            category=self.cat1, name='Screwdriver', slug='screwdriver',
            price=Decimal('9.99'), stock=5, available=True, is_online=True,
        )
        Product.objects.create(
            category=self.cat2, name='Drill', slug='drill',
            price=Decimal('89.99'), stock=3, available=True, is_online=False,
        )

    def test_list_categories_status(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_categories_returns_all(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.data['count'], 3)

    def test_category_has_expected_fields(self):
        response = self.client.get('/api/categories/')
        cat = response.data['results'][0]
        for field in ['id', 'name', 'slug', 'product_count']:
            self.assertIn(field, cat)

    def test_category_product_count_only_online_available(self):
        response = self.client.get('/api/categories/')
        cats = {c['slug']: c for c in response.data['results']}
        self.assertEqual(cats['hand-tools']['product_count'], 2)
        self.assertEqual(cats['power-tools']['product_count'], 0)
        self.assertEqual(cats['gardening']['product_count'], 0)

    def test_categories_ordered_by_name(self):
        response = self.client.get('/api/categories/')
        names = [c['name'] for c in response.data['results']]
        self.assertEqual(names, sorted(names))

    def test_categories_no_auth_required(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_count_excludes_unavailable(self):
        Product.objects.create(
            category=self.cat1, name='Broken', slug='broken',
            price=Decimal('1.00'), stock=0, available=False, is_online=True,
        )
        response = self.client.get('/api/categories/')
        cats = {c['slug']: c for c in response.data['results']}
        # hand-tools still has only its 2 available+online products
        self.assertEqual(cats['hand-tools']['product_count'], 2)

    def test_categories_ordered_alphabetically_exact(self):
        response = self.client.get('/api/categories/')
        names = [c['name'] for c in response.data['results']]
        self.assertEqual(names, ['Gardening', 'Hand Tools', 'Power Tools'])

    def test_post_not_allowed(self):
        response = self.client.post('/api/categories/', {'name': 'New', 'slug': 'new'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_pagination_fields_present(self):
        response = self.client.get('/api/categories/')
        for field in ['count', 'next', 'previous', 'results']:
            self.assertIn(field, response.data)


class CategoryEmptyAPITest(TestCase):
    """Category endpoint with no categories at all."""

    def setUp(self):
        self.client = APIClient()

    def test_empty_category_list(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])
