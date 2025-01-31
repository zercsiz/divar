"""
Tests for user API.
"""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Creates and returns a new user."""
    return get_user_model().objects.create_user(**params)


class PunlicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_successful(self):
        """Tests that the user creation is successful."""
        payload = {
            'email': 'user@example.com',
            'password': 'testpass244',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists"""
        payload = {
            'email': 'user@exaplme.com',
            'password': 'testpass123',
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test error returned if password is less than 5 characters."""
        payload = {
            'email': 'user@exaplme.com',
            'password': 'te12',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_invalid_phone_number_error(self):
        """Test return error if phone number is invalid."""
        payload = {
            'email': 'test@example.com',
            'password': 'pass125234',
            'phone_number': '6543',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = get_user_model().objects.filter(
            phone_number=payload['phone_number']).exists()
        self.assertFalse(exists)

    def test_invalid_first_name_error(self):
        """Test return error if first name is invalid."""
        payload = {
            'email': 'test@example.com',
            'password': 'pass125234',
            'first_name': '298374',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = get_user_model().objects.filter(
            first_name=payload['first_name']).exists()
        self.assertFalse(exists)

    def test_invalid_last_name_error(self):
        """Test return error if first name is invalid."""
        payload = {
            'email': 'test@example.com',
            'password': 'pass125234',
            'last_name': '>&&*vzds',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = get_user_model().objects.filter(
            last_name=payload['last_name']).exists()
        self.assertFalse(exists)

    def test_create_token_for_user(self):
        """Test generate token for valid credentials."""

        user_details = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_bad_credentials(self):
        """Test returnes error if credentials invalid"""
        create_user(email='test@example.com', password='goodpass')
        payload = {
            'email': 'test@example.com',
            'password': 'basspass'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test returns error if password is blank"""
        create_user(email='test@example.com', password='goodpass')
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication if required for retrieving user data."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='goodpass123',
            first_name='firstname',
            last_name='lastname',
            phone_number='+907776665544'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""

        res = self.client.get(ME_URL)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'phone_number': self.user.phone_number,
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_me_not_allowed(self):
        """Test post request not allowed for the me endpoint."""

        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_full_update_user_profile(self):
        """Test full update user profile for authenticated user."""

        payload = {
            'password': 'newpass123',
            'email': 'newmail@example.com',
            'first_name': 'first name',
            'last_name': 'last name',
            'phone_number': '+905337867492'
        }
        res = self.client.put(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['password']))
        payload.pop('password')
        for attr, value in payload.items():
            self.assertEqual(value, getattr(self.user, attr))

    def test_partial_update_user_profile(self):
        """Test partial update user profile for authenticated user."""

        payload = {
            'first_name': 'first name',
            'last_name': 'last name',
            'phone_number': '+905337867492'
        }
        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        for attr, value in payload.items():
            self.assertEqual(value, getattr(self.user, attr))

    def test_update_email_exists_error(self):
        """Test return error if email already exists in database."""
        create_user(email='mail@example.com', password='testpass123')
        payload = {'email': 'mail@example.com'}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user.email, payload['email'])

    def test_update_phone_number_exists_error(self):
        """Test return error if phone number exists in database."""

        user2 = create_user(
            email='email@example.com',
            password='9283uiaf',
            phone_number='+906657876543',
        )
        payload = {
            'phone_number': user2.phone_number
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user.phone_number, payload['phone_number'])
