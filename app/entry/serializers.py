"""
Serializers for entry APIs.
"""
from rest_framework import serializers
from core.models import (
    Entry,
    Category,
)


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for categories.
    """
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class EntrySerializer(serializers.ModelSerializer):
    """
    Serializer for recipes.
    """
    category = serializers.CharField()

    class Meta:
        model = Entry
        fields = ['id', 'title', 'price', 'created_at',
                  'edited_at', 'expires_at', 'address', 'phone_number',
                  'category']
        read_only_fields = ['id', 'created_at', 'edited_at',
                            'expires_at']

    def create(self, validated_data):
        """
        Create and return a new entry.
        """
        category_name = validated_data.pop('category', None)
        if not category_name:
            raise serializers.ValidationError(
                {'category': 'This field is required.'})

        try:
            category_obj = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            raise serializers.ValidationError(
                {'category': 'The specified category does not exist.'})

        entry = Entry.objects.create(**validated_data, category=category_obj)

        return entry

    def update(self, instance, validated_data):
        """
        Update and return an entry.
        """
        category_name = validated_data.pop('category', None)
        if category_name is not None:
            try:
                category_obj = Category.objects.get(
                    name=category_name)
            except Category.DoesNotExist:
                raise serializers.ValidationError(
                    {"category": "The specified category does not exist."})
            instance.category = category_obj

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class EntryDetailSerializer(EntrySerializer):
    """
    Serializer for recipe detail view.
    """
    class Meta(EntrySerializer.Meta):
        fields = EntrySerializer.Meta.fields + ['description']
