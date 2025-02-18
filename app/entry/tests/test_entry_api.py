"""
Tests for entry epi.
"""
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Entry,
    Category,
    Plan
)
from entry.serializers import EntrySerializer, EntryDetailSerializer

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


ENTRIES_URL = reverse('entry:entry-list')


def detail_url(entry_id: int):
    """
    Create and return an entry detail url.
    """
    return reverse('entry:entry-detail', args=[entry_id])


def create_user(**params) -> object:
    """
    Helper function to create and return a new user.
    """
    defaults = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'fname',
        'last_name': 'lname',
        'phone_number': '+906667775454'
    }
    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)
    return user


def create_entry(user: object, **params) -> object:
    """
    Helper function to create and return a new entry.
    """
    category, created = Category.objects.get_or_create(name='test cat')
    defaults = {
        'title': 'test entry',
        'description': 'a test description for entry',
        'price': Decimal('150.00'),
        'phone_number': '+906667775454',
        'address': 'example address, number 99',
        'category': category
    }
    defaults.update(params)
    entry = Entry.objects.create(user=user, **defaults)
    return entry


class PublicEntryApiTests(TestCase):
    """
    Test unauthenticated api requests.
    """
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test listing entries return error for unauthenticated user.
        """
        res = self.client.get(ENTRIES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recipe_detail_auth_required(self):
        """
        Test getting recipe detail returns error
        for unauthenticated user.
        """
        user = create_user()
        entry = create_entry(user=user)
        url = detail_url(entry.id)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateEntryApiTests(TestCase):
    """
    Test authenticated api requests.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_entries_success(self):
        """
        Test retrieving entries for authenticated user is successful.
        """
        user2 = create_user(email='user2@example.com')
        create_entry(user=self.user, title='entry1')
        create_entry(user=user2, title='entry2')
        res = self.client.get(ENTRIES_URL)
        entries = Entry.objects.all().order_by('-created_at')
        serializer = EntrySerializer(entries, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_entry_detail(self):
        """
        Test get recipe detail.
        """
        entry = create_entry(user=self.user)
        serializer = EntryDetailSerializer(entry)
        url = detail_url(entry.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_create_entry_successful(self):
        """
        Test creating a new entry is successful.
        """
        category_obj = Category.objects.create(name='cat1')
        payload = {
            'title': 'test entry',
            'description': 'a test description for entry',
            'price': Decimal('150.00'),
            'phone_number': '+906667775454',
            'address': 'example address, number 99',
            'category': category_obj.name
        }
        res = self.client.post(ENTRIES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        entry = Entry.objects.get(id=res.data['id'])

        # because its needed to check its the
        # object itself instead of the name
        payload.pop('category')
        for attr, value in payload.items():
            self.assertEqual(getattr(entry, attr), value)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.category, category_obj)

        self.assertEqual(entry.user.plan.name, 'Basic')

    def create_entry_without_category_error(self):
        """
        Test creating a entry without a category returns error.
        """
        payload = {
            'title': 'test entry',
            'description': 'a test description for entry',
            'price': Decimal('150.00'),
            'phone_number': '+906667775454',
            'address': 'example address, number 99',
        }
        res = self.client.post(ENTRIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = Entry.objects.get(title=payload['title'])
        self.assertFalse(exists)

    def test_create_more_than_max_entries_error(self):
        """
        Test creating more entried than max entries returns error.
        """
        plan, created = Plan.objects.get_or_create(name='Basic')
        category_obj = Category.objects.create(name='cat1')
        for _ in range(plan.max_entries):
            create_entry(user=self.user)

        payload = {
            'title': 'test entry',
            'description': 'a test description for entry',
            'price': Decimal('150.00'),
            'phone_number': '+906667775454',
            'address': 'example address, number 99',
            'category': category_obj.name
        }
        res = self.client.post(ENTRIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        entries_count = Entry.objects.filter(user=self.user).count()
        self.assertEqual(entries_count, plan.max_entries)

    def test_partial_update(self):
        """
        Test partial update is successful.
        """
        new_category_obj = Category.objects.create(name='new cat')
        entry = create_entry(user=self.user)
        url = detail_url(entry.id)
        payload = {
            'title': 'new title',
            'category': new_category_obj.name
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        entry.refresh_from_db()
        self.assertEqual(entry.title, payload['title'])
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.category, new_category_obj)

    def test_full_update(self):
        """
        Test full update is successful.
        """
        new_category_obj = Category.objects.create(name='new cat')
        entry = create_entry(user=self.user)
        url = detail_url(entry.id)
        payload = {
            'title': 'new entry',
            'description': 'a new test description for entry',
            'price': Decimal('100.00'),
            'phone_number': '+906667779999',
            'address': 'some new address',
            'category': new_category_obj.name
        }
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        entry.refresh_from_db()
        self.assertEqual(entry.user, self.user)
        payload.pop('category')
        for attr, value in payload.items():
            self.assertEqual(getattr(entry, attr), value)
        self.assertEqual(entry.category, new_category_obj)

    def test_update_user_returns_error(self):
        """
        Test updating an entrys user returns error.
        """
        entry = create_entry(user=self.user)
        user2 = create_user(email='user2@example.com')
        url = detail_url(entry.id)
        payload = {
            'user': user2.id
        }
        self.client.patch(url, payload)
        entry.refresh_from_db()
        self.assertEqual(entry.user, self.user)

    def test_update_other_users_entry_returns_error(self):
        """
        Test updating other users entry returns error.
        """
        other_user = create_user(email='other@example.com')
        entry = create_entry(user=other_user)
        url = detail_url(entry.id)
        payload = {
            'title': 'its mine now'
        }
        res = self.client.patch(url, payload)
        entry.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(entry.title, payload['title'])

    def test_delete_entry(self):
        """
        Test deleting an entry is successful.
        """
        entry = create_entry(user=self.user)
        url = detail_url(entry.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = Entry.objects.filter(user=self.user).exists()
        self.assertFalse(exists)

    def test_delete_other_users_entry_returns_error(self):
        """
        Test deleting other users entry returns error.
        """
        other_user = create_user(email='other@example.com')
        entry = create_entry(user=other_user)
        url = detail_url(entry.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Entry.objects.filter(user=other_user).exists())
