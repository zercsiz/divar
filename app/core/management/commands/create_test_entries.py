from django.core.management.base import BaseCommand, CommandError
from core.models import Entry, Category
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.db import IntegrityError


class Command(BaseCommand):
    """
    Command to create 200 test entries for testing pagination.
    """
    def handle(self, *args, **options):
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        try:
            for i in range(1, 201):
                category, created = Category.objects.get_or_create(name='Misc')
                phone_number = 1111111111
                Entry.objects.create(
                    user=user,
                    title=f'test title {i}',
                    description=f'test description {i}',
                    price=Decimal(f'{i}.00'),
                    phone_number=f'+90{phone_number+i}',
                    category=category,

                )
        except IntegrityError:
            raise CommandError("An error occured")

        self.stdout.write(self.style.SUCCESS(
            'Operation successful.'
        ))
