"""
Tests for user API.
"""
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from datetime import date

from core.models import Plan

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """
    Creates and returns a new user.
    """
    return get_user_model().objects.create_user(**params)


class PunlicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_successful(self):
        """
        Tests that the user creation is successful.
        """
        payload = {
            'email': 'user@example.com',
            'password': 'testpass244',
            'date_of_birth': '2000-01-01'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertEqual(
            user.date_of_birth,
            date.fromisoformat(payload['date_of_birth']))
        self.assertNotIn('password', res.data)

    def test_created_users_have_basic_plan(self):
        """
        Test basic plan is automatically assigned to users upon creation.
        """
        payload = {
            'email': 'user@example.com',
            'password': 'testpass244',
            'date_of_birth': '2000-01-01'
        }
        self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual('Basic', user.plan.name)
        plan_exists = Plan.objects.filter(name='Basic')
        plan = Plan.objects.get(name='Basic')
        self.assertTrue(plan_exists)
        self.assertEqual(user.plan.max_entries, plan.max_entries)

    def test_user_with_email_exists_error(self):
        """
        Test error returned if user with email exists.
        """
        payload = {
            'email': 'user@exaplme.com',
            'password': 'testpass123',
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """
        Test error returned if password is less than 5 characters.
        """
        payload = {
            'email': 'user@exaplme.com',
            'password': 'te12',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_user_without_date_of_birth_error(self):
        """
        Test return error if date of birth is not sent.
        """
        payload = {
            'email': 'test@example.com',
            'password': 'test1234',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(exists)

    def test_create_user_with_invalid_date_of_birth_error(self):
        """
        Test return error if date of birth is invalid.
        """
        payload = {
            'email': 'test@example.com',
            'password': 'test1234',
            'date_of_birth': 'invalid'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(exists)

    def test_invalid_phone_number_error(self):
        """
        Test return error if phone number is invalid.
        """
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
        """
        Test return error if first name is invalid.
        """
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
        """
        Test return error if first name is invalid.
        """
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

    def test_user_under_18_error(self):
        """
        Test return error if user under 18.
        """
        # cannot harcode a date because in time it will eventually
        # be more than 18 years old
        less_than_18_year = date.today().year - 16

        payload = {
            'email': 'test@example.com',
            'password': 'test1234',
            'date_of_birth': f'{less_than_18_year}-04-20',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = get_user_model().objects.filter(
            date_of_birth=date.fromisoformat(
                payload['date_of_birth'])).exists()
        self.assertFalse(exists)

    def test_user_too_old_error(self):
        """
        Test return error if user is too old (more than 100).
        """
        payload = {
            'email': 'test@example.com',
            'password': 'test1234',
            'date_of_birth': '1923-04-20',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = get_user_model().objects.filter(
            date_of_birth=date.fromisoformat(
                payload['date_of_birth'])).exists()
        self.assertFalse(exists)

    def test_create_token_for_user(self):
        """
        Test generate token for valid credentials.
        """

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
        """
        Test returnes error if credentials invalid.
        """
        create_user(email='test@example.com', password='goodpass')
        payload = {
            'email': 'test@example.com',
            'password': 'basspass'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """
        Test returns error if password is blank.
        """
        create_user(email='test@example.com', password='goodpass')
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Test authentication if required for retrieving user data.
        """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test API requests that require authentication.
    """

    def setUp(self):
        year_of_birth = date.today().year - 20
        date_of_birth = date(year_of_birth, 1, 1)
        self.user = create_user(
            email='test@example.com',
            password='goodpass123',
            first_name='firstname',
            last_name='lastname',
            phone_number='+907776665544',
            date_of_birth=date_of_birth
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test retrieving profile for logged in user.
        """

        res = self.client.get(ME_URL)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'phone_number': self.user.phone_number,
            'date_of_birth': self.user.date_of_birth.strftime('%Y-%m-%d'),
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_me_not_allowed(self):
        """
        Test post request not allowed for the me endpoint.
        """

        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_full_update_user_profile(self):
        """
        Test full update user profile for authenticated user.
        """

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
        """
        Test partial update user profile for authenticated user.
        """

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
        """
        Test return error if email already exists in database.
        """
        create_user(email='mail@example.com', password='testpass123')
        payload = {'email': 'mail@example.com'}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user.email, payload['email'])

    def test_update_phone_number_exists_error(self):
        """
        Test return error if phone number exists in database.
        """

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

    def test_update_date_of_birth_error(self):
        """
        Test updating date of birth returns error.
        """
        payload = {
            'date_of_birth': '2001-02-02'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user.date_of_birth,
                            date.fromisoformat(payload['date_of_birth']))
