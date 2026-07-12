"""
API Review Tests
Tests for product review listing, creation, duplicate prevention,
authentication requirements, and validation via /api/products/<id>/reviews/ endpoints.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from products.models import Category, Product, ProductReview


class ReviewListAPITest(TestCase):
    """Tests for GET /api/products/{id}/reviews/"""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Saw', slug='saw',
            price=Decimal('29.99'), stock=5, available=True, is_online=True,
        )
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        ProductReview.objects.create(
            product=self.product, user=self.user1,
            rating=5, comment='Excellent!',
        )
        ProductReview.objects.create(
            product=self.product, user=self.user2,
            rating=3, comment='Average.',
        )

    def test_list_reviews_status(self):
        response = self.client.get(f'/api/products/{self.product.id}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_reviews_count(self):
        response = self.client.get(f'/api/products/{self.product.id}/reviews/')
        self.assertEqual(response.data['count'], 2)

    def test_review_has_expected_fields(self):
        response = self.client.get(f'/api/products/{self.product.id}/reviews/')
        review = response.data['results'][0]
        for field in ['id', 'user', 'rating', 'title', 'comment', 'verified_purchase', 'created']:
            self.assertIn(field, review)

    def test_list_reviews_for_product_with_no_reviews(self):
        other = Product.objects.create(
            category=self.cat, name='Axe', slug='axe',
            price=Decimal('39.99'), stock=2, available=True, is_online=True,
        )
        response = self.client.get(f'/api/products/{other.id}/reviews/')
        self.assertEqual(response.data['count'], 0)

    def test_list_reviews_no_auth_required(self):
        response = self.client.get(f'/api/products/{self.product.id}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReviewCreateAPITest(TestCase):
    """Tests for POST /api/products/{id}/reviews/create/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='reviewer', password='pass123')
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Saw', slug='saw',
            price=Decimal('29.99'), stock=5, available=True, is_online=True,
        )

    def test_create_review_unauthenticated(self):
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'comment': 'Great!'},
        )
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])

    def test_create_review_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'comment': 'Great product!'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductReview.objects.count(), 1)

    def test_create_review_sets_user(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 4, 'comment': 'Good.'},
        )
        review = ProductReview.objects.first()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.product)

    def test_create_review_missing_rating(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'comment': 'No rating provided.'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_missing_comment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_rating_zero(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 0, 'comment': 'Invalid.'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_rating_six(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 6, 'comment': 'Too high.'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_review_rejected(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'comment': 'First review.'},
        )
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 3, 'comment': 'Second review.'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ProductReview.objects.count(), 1)

    def test_create_review_for_offline_product(self):
        self.product.is_online = False
        self.product.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'comment': 'Should fail.'},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_review_for_nonexistent_product(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/products/99999/reviews/create/',
            {'rating': 5, 'comment': 'No product.'},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_review_with_title(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'title': 'Amazing!', 'comment': 'Highly recommend.'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Amazing!')

    def test_create_review_with_token_auth(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 4, 'comment': 'Token auth test.'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_review_rating_min_boundary(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 1, 'comment': 'Lowest valid rating.'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_review_rating_max_boundary(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'comment': 'Highest valid rating.'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_review_defaults_not_verified(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 4, 'comment': 'Default flags.'},
        )
        review = ProductReview.objects.first()
        self.assertFalse(review.verified_purchase)

    def test_create_review_verified_purchase_read_only(self):
        """Client cannot set verified_purchase via the API."""
        self.client.force_authenticate(user=self.user)
        self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'comment': 'Trying to cheat.', 'verified_purchase': True},
        )
        review = ProductReview.objects.first()
        self.assertFalse(review.verified_purchase)

    def test_create_review_invalid_token_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        response = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'comment': 'Bad token.'},
        )
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])

    def test_two_users_can_review_same_product(self):
        u2 = User.objects.create_user(username='reviewer2', password='pass123')
        self.client.force_authenticate(user=self.user)
        r1 = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 5, 'comment': 'User one.'},
        )
        self.client.force_authenticate(user=u2)
        r2 = self.client.post(
            f'/api/products/{self.product.id}/reviews/create/',
            {'rating': 3, 'comment': 'User two.'},
        )
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductReview.objects.count(), 2)


class ReviewListOrderingAPITest(TestCase):
    """Ordering and isolation coverage for GET /api/products/{id}/reviews/."""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.cat, name='Saw', slug='saw',
            price=Decimal('29.99'), stock=5, available=True, is_online=True,
        )
        self.other = Product.objects.create(
            category=self.cat, name='Axe', slug='axe',
            price=Decimal('39.99'), stock=2, available=True, is_online=True,
        )
        self.u1 = User.objects.create_user(username='u1', password='pass123')
        self.u2 = User.objects.create_user(username='u2', password='pass123')

    def test_reviews_newest_first(self):
        ProductReview.objects.create(
            product=self.product, user=self.u1, rating=3,
            title='Older', comment='First.',
        )
        ProductReview.objects.create(
            product=self.product, user=self.u2, rating=4,
            title='Newer', comment='Second.',
        )
        response = self.client.get(f'/api/products/{self.product.id}/reviews/')
        self.assertEqual(response.data['results'][0]['title'], 'Newer')

    def test_reviews_isolated_per_product(self):
        ProductReview.objects.create(product=self.product, user=self.u1, rating=5, comment='For saw.')
        ProductReview.objects.create(product=self.other, user=self.u1, rating=2, comment='For axe.')
        response = self.client.get(f'/api/products/{self.product.id}/reviews/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['comment'], 'For saw.')
