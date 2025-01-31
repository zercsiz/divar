"""
Views for recipe APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Entry
from entry import serializers

from django.utils.timezone import make_aware

from datetime import datetime
from dateutil.relativedelta import relativedelta
import os


class EntryViewSet(viewsets.ModelViewSet):
    """
    View for manage entry APIs.
    """
    serializer_class = serializers.EntryDetailSerializer
    queryset = Entry.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve entries ordered by date and time.
        """
        # users are allowed to list and retrieve others entries
        # but not allowed to preform delete or update operations
        # on other users entries
        if self.action == 'list' or self.action == 'retrieve':
            return self.queryset.all().order_by('-created_at')

        return self.queryset.filter(
            user=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        """
        Return the serializer class for the request.
        """

        if self.action == 'list':
            return serializers.EntrySerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new entry."""

        # expiration date is retrieved from environment variable in dockerfile
        exp_months = int(os.getenv('ENTRY_EXPIRATION_MONTHS'))
        serializer.save(
            user=self.request.user,
            expires_at=make_aware(
                datetime.now()) + relativedelta(months=exp_months)
        )
