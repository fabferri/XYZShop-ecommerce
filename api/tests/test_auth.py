"""
API Authentication Tests
Tests for user registration, login, token generation, and profile retrieval
via /api/auth/ endpoints.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token


class RegisterAPITest(TestCase):
    """Tests for POST /api/auth/register/"""

    def setUp(self):
        self.client = APIClient()
        self.reg_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'strongpass123',
        }

    def test_register_success(self):
        response = self.client.post('/api/auth/register/', self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_returns_token(self):
        response = self.client.post('/api/auth/register/', self.reg_data)
        self.assertIn('token', response.data)
        self.assertTrue(len(response.data['token']) > 0)

    def test_register_returns_user_profile(self):
        response = self.client.post('/api/auth/register/', self.reg_data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertEqual(response.data['user']['email'], 'new@example.com')

    def test_register_creates_user(self):
        self.client.post('/api/auth/register/', self.reg_data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_is_hashed(self):
        self.client.post('/api/auth/register/', self.reg_data)
        user = User.objects.get(username='newuser')
        self.assertNotEqual(user.password, 'strongpass123')
        self.assertTrue(user.check_password('strongpass123'))

    def test_register_duplicate_username(self):
        User.objects.create_user(username='newuser', password='otherpass123')
        response = self.client.post('/api/auth/register/', self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_username(self):
        data = self.reg_data.copy()
        del data['username']
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password(self):
        data = self.reg_data.copy()
        del data['password']
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password(self):
        data = self.reg_data.copy()
        data['password'] = 'short'
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_not_in_response(self):
        response = self.client.post('/api/auth/register/', self.reg_data)
        self.assertNotIn('password', response.data.get('user', {}))

    def test_register_creates_token_in_db(self):
        response = self.client.post('/api/auth/register/', self.reg_data)
        user = User.objects.get(username='newuser')
        self.assertTrue(Token.objects.filter(user=user).exists())
        self.assertEqual(Token.objects.get(user=user).key, response.data['token'])

    def test_register_stores_profile_fields(self):
        self.client.post('/api/auth/register/', self.reg_data)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.email, 'new@example.com')

    def test_register_get_not_allowed(self):
        response = self.client.get('/api/auth/register/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_register_password_min_length_boundary(self):
        data = self.reg_data.copy()
        data['username'] = 'boundaryuser'
        data['password'] = '12345678'  # exactly 8 chars -> valid
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginAPIExtraTest(TestCase):
    """Additional login coverage."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@example.com',
        )

    def test_login_token_matches_stored_token(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser', 'password': 'testpass123',
        })
        stored = Token.objects.get(user=self.user)
        self.assertEqual(response.data['token'], stored.key)

    def test_login_token_usable_for_protected_endpoint(self):
        login = self.client.post('/api/auth/login/', {
            'username': 'testuser', 'password': 'testpass123',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        profile = self.client.get('/api/auth/profile/')
        self.assertEqual(profile.status_code, status.HTTP_200_OK)

    def test_login_empty_username_value(self):
        response = self.client.post('/api/auth/login/', {
            'username': '', 'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileAPIExtraTest(TestCase):
    """Additional profile coverage."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@example.com',
        )

    def test_profile_invalid_token_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token doesnotexist')
        response = self.client.get('/api/auth/profile/')
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])

    def test_profile_reflects_authenticated_user(self):
        other = User.objects.create_user(username='other', password='pass123')
        self.client.force_authenticate(user=other)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.data['username'], 'other')


class LoginAPITest(TestCase):
    """Tests for POST /api/auth/login/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            email='test@example.com',
        )

    def test_login_success(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser', 'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_returns_token(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser', 'password': 'testpass123',
        })
        self.assertIn('token', response.data)

    def test_login_returns_user_profile(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser', 'password': 'testpass123',
        })
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_same_token_on_multiple_logins(self):
        r1 = self.client.post('/api/auth/login/', {
            'username': 'testuser', 'password': 'testpass123',
        })
        r2 = self.client.post('/api/auth/login/', {
            'username': 'testuser', 'password': 'testpass123',
        })
        self.assertEqual(r1.data['token'], r2.data['token'])

    def test_login_wrong_password(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser', 'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'noone', 'password': 'nopass',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_username(self):
        response = self.client.post('/api/auth/login/', {
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_body(self):
        response = self.client.post('/api/auth/login/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_get_method_not_allowed(self):
        response = self.client.get('/api/auth/login/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ProfileAPITest(TestCase):
    """Tests for GET /api/auth/profile/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            email='test@example.com', first_name='Test', last_name='User',
        )

    def test_profile_unauthenticated(self):
        response = self.client.get('/api/auth/profile/')
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_has_expected_fields(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/profile/')
        for field in ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']:
            self.assertIn(field, response.data)

    def test_profile_correct_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')

    def test_profile_with_token_auth(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_profile_post_not_allowed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/auth/profile/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
