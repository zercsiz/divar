from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,
)
from django.conf import settings


class Plan(models.Model):
    """
    Plan object.
    """
    name = models.CharField(max_length=255)
    max_entries = models.IntegerField(default=3)
    days_to_expire = models.IntegerField(default=30)

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
            raise ValueError("User must have an Email Address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)

        plan, created = Plan.objects.get_or_create(name='Basic')
        user.plan = plan
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create, save and return a new superuser.
        """
        superuser = self.create_user(email, password)
        superuser.is_staff = True
        superuser.is_superuser = True

        # because plan is for users
        superuser.plan = None
        superuser.save(using=self._db)
        return superuser


def get_default_plan_id() -> int:
    """
    creates or gets the default plan
    to be used as a default for plan field in user model.
    """
    plan, created = Plan.objects.get_or_create(name='Basic')
    return plan.id


class User(AbstractBaseUser, PermissionsMixin):
    """
    User Object.
    """
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
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
        related_name="custom_user_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
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
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    is_expired = models.BooleanField(default=False)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
