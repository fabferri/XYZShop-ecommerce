"""
API Product Tests
Tests for product listing, detail, search, filtering by category,
ordering, pagination, and online/available visibility via /api/products/ endpoints.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product, ProductReview


class ProductListAPITest(TestCase):
    """Tests for GET /api/products/"""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.cat2 = Category.objects.create(name='Fasteners', slug='fasteners')
        self.p1 = Product.objects.create(
            category=self.cat, name='Hammer', slug='hammer',
            price=Decimal('19.99'), stock=10, available=True, is_online=True,
        )
        self.p2 = Product.objects.create(
            category=self.cat, name='Saw', slug='saw',
            price=Decimal('29.99'), stock=5, available=True, is_online=True,
        )
        self.p_offline = Product.objects.create(
            category=self.cat, name='Hidden Item', slug='hidden-item',
            price=Decimal('9.99'), stock=1, available=True, is_online=False,
        )
        self.p_unavailable = Product.objects.create(
            category=self.cat, name='Out of Stock', slug='out-of-stock',
            price=Decimal('49.99'), stock=0, available=False, is_online=True,
        )
        self.p3 = Product.objects.create(
            category=self.cat2, name='Bolt Set', slug='bolt-set',
            price=Decimal('5.99'), stock=100, available=True, is_online=True,
        )

    def test_list_products_status(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_products_excludes_offline(self):
        response = self.client.get('/api/products/')
        names = [p['name'] for p in response.data['results']]
        self.assertNotIn('Hidden Item', names)

    def test_list_products_excludes_unavailable(self):
        response = self.client.get('/api/products/')
        names = [p['name'] for p in response.data['results']]
        self.assertNotIn('Out of Stock', names)

    def test_list_products_includes_available_online(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.data['count'], 3)

    def test_product_list_has_expected_fields(self):
        response = self.client.get('/api/products/')
        product = response.data['results'][0]
        expected_fields = [
            'id', 'name', 'slug', 'image', 'price',
            'category', 'available', 'average_rating', 'rating_count',
        ]
        for field in expected_fields:
            self.assertIn(field, product)

    def test_product_list_no_description(self):
        """List serializer should not include description (detail only)."""
        response = self.client.get('/api/products/')
        product = response.data['results'][0]
        self.assertNotIn('description', product)

    def test_filter_by_category_slug(self):
        response = self.client.get('/api/products/?category__slug=fasteners')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Bolt Set')

    def test_filter_by_category_slug_no_results(self):
        response = self.client.get('/api/products/?category__slug=nonexistent')
        self.assertEqual(response.data['count'], 0)

    def test_search_by_name(self):
        response = self.client.get('/api/products/?search=Hammer')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Hammer')

    def test_search_case_insensitive(self):
        response = self.client.get('/api/products/?search=hammer')
        self.assertEqual(response.data['count'], 1)

    def test_search_no_results(self):
        response = self.client.get('/api/products/?search=NonexistentProduct')
        self.assertEqual(response.data['count'], 0)

    def test_search_by_description(self):
        self.p1.description = 'A heavy-duty steel hammer'
        self.p1.save()
        response = self.client.get('/api/products/?search=steel')
        self.assertEqual(response.data['count'], 1)

    def test_ordering_by_price_asc(self):
        response = self.client.get('/api/products/?ordering=price')
        prices = [Decimal(p['price']) for p in response.data['results']]
        self.assertEqual(prices, sorted(prices))

    def test_ordering_by_price_desc(self):
        response = self.client.get('/api/products/?ordering=-price')
        prices = [Decimal(p['price']) for p in response.data['results']]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_ordering_by_name(self):
        response = self.client.get('/api/products/?ordering=name')
        names = [p['name'] for p in response.data['results']]
        self.assertEqual(names, sorted(names))

    def test_default_ordering_is_name(self):
        response = self.client.get('/api/products/')
        names = [p['name'] for p in response.data['results']]
        self.assertEqual(names, sorted(names))

    def test_pagination_present(self):
        response = self.client.get('/api/products/')
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_no_auth_required(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductDetailAPITest(TestCase):
    """Tests for GET /api/products/{id}/"""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.user = User.objects.create_user(username='reviewer', password='pass123')
        self.product = Product.objects.create(
            category=self.cat, name='Hammer', slug='hammer',
            description='A solid hammer for nails.',
            price=Decimal('19.99'), stock=10, available=True, is_online=True,
        )
        self.review = ProductReview.objects.create(
            product=self.product, user=self.user,
            rating=4, title='Good tool', comment='Works well.',
        )

    def test_detail_status(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_has_all_fields(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        expected = [
            'id', 'name', 'slug', 'image', 'description', 'price', 'stock',
            'available', 'category', 'average_rating', 'rating_count',
            'reviews', 'created', 'updated',
        ]
        for field in expected:
            self.assertIn(field, response.data)

    def test_detail_includes_description(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.data['description'], 'A solid hammer for nails.')

    def test_detail_category_is_nested(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        cat = response.data['category']
        self.assertIn('id', cat)
        self.assertIn('name', cat)
        self.assertIn('slug', cat)

    def test_detail_includes_reviews(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(len(response.data['reviews']), 1)
        self.assertEqual(response.data['reviews'][0]['rating'], 4)

    def test_detail_average_rating(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.data['average_rating'], 4.0)

    def test_detail_rating_count(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.data['rating_count'], 1)

    def test_detail_product_not_found(self):
        response = self.client.get('/api/products/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_offline_product_not_found(self):
        self.product.is_online = False
        self.product.save()
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_unavailable_product_not_found(self):
        self.product.available = False
        self.product.save()
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_no_reviews_empty_list(self):
        self.review.delete()
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.data['reviews'], [])
        self.assertEqual(response.data['average_rating'], 0.0)
        self.assertEqual(response.data['rating_count'], 0)

    def test_detail_average_rating_multiple_reviews(self):
        u2 = User.objects.create_user(username='reviewer2', password='pass123')
        u3 = User.objects.create_user(username='reviewer3', password='pass123')
        ProductReview.objects.create(product=self.product, user=u2, rating=2, comment='Meh.')
        ProductReview.objects.create(product=self.product, user=u3, rating=5, comment='Great.')
        response = self.client.get(f'/api/products/{self.product.id}/')
        # (4 + 2 + 5) / 3 = 3.666...
        self.assertEqual(response.data['rating_count'], 3)
        self.assertAlmostEqual(float(response.data['average_rating']), 3.7, places=1)

    def test_detail_reviews_newest_first(self):
        u2 = User.objects.create_user(username='reviewer2', password='pass123')
        ProductReview.objects.create(
            product=self.product, user=u2, rating=1,
            title='Newer', comment='Latest review.',
        )
        response = self.client.get(f'/api/products/{self.product.id}/')
        # Meta ordering is ('-created',) -> newest first
        self.assertEqual(response.data['reviews'][0]['title'], 'Newer')

    def test_detail_price_is_string(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.data['price'], '19.99')

    def test_detail_stock_value(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.data['stock'], 10)


class ProductListExtraAPITest(TestCase):
    """Additional coverage for GET /api/products/ (search, filters, pagination)."""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')

    def _make(self, name, slug, price='10.00', **kwargs):
        return Product.objects.create(
            category=self.cat, name=name, slug=slug,
            price=Decimal(price), stock=5,
            available=kwargs.get('available', True),
            is_online=kwargs.get('is_online', True),
            description=kwargs.get('description', ''),
        )

    def test_search_matches_multiple_products(self):
        self._make('Power Drill', 'power-drill')
        self._make('Hand Drill', 'hand-drill')
        self._make('Hammer', 'hammer')
        response = self.client.get('/api/products/?search=drill')
        self.assertEqual(response.data['count'], 2)

    def test_search_empty_query_returns_all(self):
        self._make('A', 'a')
        self._make('B', 'b')
        response = self.client.get('/api/products/?search=')
        self.assertEqual(response.data['count'], 2)

    def test_filter_available_true(self):
        self._make('Visible', 'visible', available=True)
        response = self.client.get('/api/products/?available=true')
        self.assertEqual(response.data['count'], 1)

    def test_category_is_string_in_list(self):
        self._make('Wrench', 'wrench')
        response = self.client.get('/api/products/')
        self.assertEqual(response.data['results'][0]['category'], 'Tools')

    def test_price_is_string_in_list(self):
        self._make('Wrench', 'wrench', price='14.50')
        response = self.client.get('/api/products/')
        self.assertEqual(response.data['results'][0]['price'], '14.50')

    def test_combined_search_and_ordering(self):
        self._make('Drill A', 'drill-a', price='30.00')
        self._make('Drill B', 'drill-b', price='10.00')
        self._make('Drill C', 'drill-c', price='20.00')
        response = self.client.get('/api/products/?search=drill&ordering=price')
        prices = [Decimal(p['price']) for p in response.data['results']]
        self.assertEqual(prices, [Decimal('10.00'), Decimal('20.00'), Decimal('30.00')])

    def test_ordering_by_created(self):
        self._make('First', 'first')
        self._make('Second', 'second')
        response = self.client.get('/api/products/?ordering=created')
        names = [p['name'] for p in response.data['results']]
        self.assertEqual(names[0], 'First')

    def test_pagination_page_size_20(self):
        for i in range(25):
            self._make(f'Product {i:02d}', f'product-{i:02d}')
        response = self.client.get('/api/products/')
        self.assertEqual(len(response.data['results']), 20)
        self.assertEqual(response.data['count'], 25)
        self.assertIsNotNone(response.data['next'])

    def test_pagination_second_page(self):
        for i in range(25):
            self._make(f'Product {i:02d}', f'product-{i:02d}')
        response = self.client.get('/api/products/?page=2')
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNotNone(response.data['previous'])

    def test_pagination_invalid_page_404(self):
        self._make('Only', 'only')
        response = self.client.get('/api/products/?page=99')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_catalog_returns_zero(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

    def test_post_not_allowed_on_list(self):
        response = self.client.post('/api/products/', {'name': 'X'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
