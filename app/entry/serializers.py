"""
Serializers for entry APIs.
"""
from rest_framework import serializers
from core.models import Entry


class EntrySerializer(serializers.ModelSerializer):
    """
    Serializer for recipes.
    """
    class Meta:
        model = Entry
        fields = ['id', 'title', 'price', 'created_at',
                  'edited_at', 'expires_at', 'address', 'phone_number']
        read_only_fields = ['id', 'created_at', 'edited_at', 'expires_at']


class EntryDetailSerializer(EntrySerializer):
    """
    Serializer for recipe detail view.
    """
    class Meta(EntrySerializer.Meta):
        fields = EntrySerializer.Meta.fields + ['description']
