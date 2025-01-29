"""Serializers for the user API View"""

from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _

from rest_framework import serializers

import re


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object
    """

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'phone_number'
        ]
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def validate_first_name(self, value):
        """
        Check that first name is all letters.
        """
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError("Invalid first name.")
        return value

    def validate_last_name(self, value):
        """
        Check that first name is all letters.
        """
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError("Invalid last name.")
        return value

    def validate_phone_number(self, value):
        """
        Check that phone number is valid with country code
        and if it exists already in database.
        """
        regex = r'^\+?[1-9]\d{11,14}$'
        if not re.match(regex, value):
            raise serializers.ValidationError("Invalid phone number.")

        exists = get_user_model().objects.filter(
            phone_number=value).exists()
        if exists:
            raise serializers.ValidationError("Invalid phone number.")
        return value

    def create(self, validated_data):
        """
        Create and return a user with encrypted password.
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return a  user.
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for user auth token.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Validate and authenticate the user.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )
        if not user:
            message = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(message, code='authentication')

        attrs['user'] = user
        return attrs
