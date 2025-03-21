"""
Serializers for entry APIs.
"""
from rest_framework import serializers
from core.models import (
    Entry,
    Category,
    EntryImage,
)


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for categories.
    """
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class EntryImageSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading images to entries.
    """
    class Meta:
        model = EntryImage
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
        extra_kwargs = {'image': {'required': 'True'}}


class EntrySerializer(serializers.ModelSerializer):
    """
    Serializer for recipes.
    """
    category = serializers.CharField()
    images = EntryImageSerializer(many=True,
                                  required=False)

    class Meta:
        model = Entry
        fields = ['id', 'title', 'price', 'created_at',
                  'is_expired', 'category', 'images']
        read_only_fields = ['id', 'created_at', 'is_expired']

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
        fields = EntrySerializer.Meta.fields + ['description', 'phone_number']
