from celery import shared_task
from django.utils.timezone import now
from core.models import Entry


@shared_task
def mark_expired_entries():
    entries = Entry.objects.filter(is_expired=False,
                                   user__plan__isnull=False,
                                   user__plan__isblank=False)
    for entry in entries:
        if (now() - entry.created_at).days >= entry.user.plan.days_to_expire:
            entry.is_expired = True
            entry.save()
