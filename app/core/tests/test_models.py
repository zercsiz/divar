""""
Tests for models.
"""

from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from decimal import Decimal
from core import models


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """
        Test creating user with email is successful.
        """
        email = "user@example.com"
        password = "testpassword87"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

        plan = models.Plan.objects.get(name='Basic')
        self.assertEqual(user.plan, plan)

    def test_new_user_email_normalized(self):
        """
        Test email is normalized for new users.
        """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """
        Test that creating a user without an email raises a ValueError.
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """
        Test creating a superuser
        """

        user = get_user_model().objects.create_superuser(
            'user@example.com',
            'passwsnsjsj2'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_superuser)

    def test_create_entry(self):
        """
        Test creating recipe is successful.
        """
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='goodpass123',
        )
        category_obg = models.Category.objects.create(name='clothing')
        entry = models.Entry.objects.create(
            user=user,
            title='test entry',
            description='a test description for entry',
            price=Decimal('150.00'),
            phone_number='+906667775454',
            address='example address, number 99',
            category=category_obg
        )
        self.assertEqual(str(entry), entry.title)

    def test_create_category(self):
        """
        Test creating a new category is successful.
        """
        category = models.Category.objects.create(name='cat1')
        self.assertEqual(str(category), category.name)

    @patch('core.models.uuid.uuid4')
    def test_entry_file_name_uuid(self, mock_uuid):
        """
        Test generating image path.
        """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.entry_image_file_path(None, 'example.jpg')
        self.assertEqual(file_path, f'uploads/entry/{uuid}.jpg')
