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
from rest_framework.pagination import PageNumberPagination

from core.models import (
    Entry,
    EntryImage,
)
from entry import serializers


class EntryListPagination(PageNumberPagination):
    """
    Pagination for listing entries.
    """
    page_size = 30


class EntryViewSet(viewsets.ModelViewSet):
    """
    View for manage entry APIs.
    """
    serializer_class = serializers.EntryDetailSerializer
    queryset = Entry.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = EntryListPagination

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

        if self.action == 'list_user_entries':
            return self.queryset.filter(
                user=self.request.user).order_by('-created_at')

        return self.queryset.filter(
            user=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        """
        Return the serializer class for the request.
        """

        if self.action == 'list' or self.action == 'list_user_entries':
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
        Upload multiple images to an entry.
        """
        entry = self.get_object()
        images = request.FILES.getlist('images')

        if not images:
            return Response({'error': 'No images provided'},
                            status=status.HTTP_400_BAD_REQUEST)

        # user is not allowed to upload images more than
        # max_entry_images specified in their plan
        max_entry_images = request.user.plan.max_entry_images
        if len(images) > max_entry_images:
            return Response(
                {'message': f'Maximum images allowed: {max_entry_images}'},
                status=status.HTTP_400_BAD_REQUEST)

        image_instances = [EntryImage(
            image=image, entry=entry) for image in images]
        EntryImage.objects.bulk_create(image_instances)

        return Response({'message': 'Images uploaded successfully'},
                        status=status.HTTP_201_CREATED)

    @action(methods=['GET'], detail=False, url_path='user-entries')
    def list_user_entries(self, resuqest):
        """
        Action to retrieve user's entries.
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
