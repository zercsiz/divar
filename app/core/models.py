"""
Database models.
"""

import uuid
import os

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,
)
from django.conf import settings


def entry_image_file_path(instance, filename):
    """
    Generate file path for new EntryImage.
    """
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'entry', filename)


class Plan(models.Model):
    """
    Plan object.
    """
    name = models.CharField(max_length=255)
    max_entries = models.IntegerField(default=3)
    days_to_expire = models.IntegerField(default=30)
    max_entry_images = models.IntegerField(default=4)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """
    Manager for User.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create, save and return a new user.
        """
        if not email:
            raise ValueError('User must have an Email Address.')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create, save and return a new superuser.
        """
        superuser = self.create_user(email, password)
        superuser.is_staff = True
        superuser.is_superuser = True

        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    """
    User Object.
    """
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True
    )

    objects = UserManager()


class Category(models.Model):
    """
    Category object.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Entry(models.Model):
    """
    Entry object.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entries'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    is_expired = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15)
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='entries')

    def __str__(self):
        return self.title


class EntryImage(models.Model):
    """
    Image object.
    """
    entry = models.ForeignKey(Entry,
                              on_delete=models.CASCADE,
                              related_name='images')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=entry_image_file_path)

    def __str__(self):
        return (f"""Image for Entry {self.entry.id}, uploaded on
                {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}""")
