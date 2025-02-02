from django.core.management.base import BaseCommand, CommandError
from core.models import Entry, Category
from django.core.management import call_command
from django.db import IntegrityError, OperationalError, DatabaseError


class Command(BaseCommand):
    """
    Django command to populate null category field
    in existing entry objects.
    """
    def handle(self, *args, **options):
        """
        Entrypoint for command.
        """
        call_command('wait_for_db')
        try:
            category_obj, created = Category.objects.get_or_create(
                name="Miscellaneous")
        except IntegrityError:
            raise CommandError('Category object creation failed.')

        self.stdout.write(
            'Filtering entry objects with null category field...')
        try:
            entries = Entry.objects.filter(category=None)
        except (OperationalError, DatabaseError):
            raise CommandError('Filtering entries failed.')

        if entries:
            for entry in entries:
                entry.category = category_obj
                entry.save()
        else:
            raise CommandError(
                'No entries with null category field were found.')

        self.stdout.write(self.style.SUCCESS(
            'Operation successful.'
        ))
