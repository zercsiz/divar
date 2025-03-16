"""
Views for recipe APIs.
"""
from rest_framework import (
    viewsets,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from core.models import Entry
from entry import serializers


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
            return self.queryset.filter(
                is_expired=False).order_by('-created_at')

        return self.queryset.filter(
            user=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        """
        Return the serializer class for the request.
        """

        if self.action == 'list':
            return serializers.EntrySerializer
        elif self.action == 'upload_image':
            return serializers.EntryImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new entry.
        """
        user_entries_count = Entry.objects.filter(
            user=self.request.user).count()
        max_entries = self.request.user.plan.max_entries
        if user_entries_count == max_entries:
            raise ValidationError(
                f'User has reached the maximum of {max_entries} entries.')

        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """
        Upload an image to entry.
        """
        entry = self.get_object()
        serializer = self.get_serializer(entry, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
