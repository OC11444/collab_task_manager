"""
Users module serializers.

Author: Mich omolo
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class IdPSyncSerializer(serializers.Serializer):
    """
    Handles user data coming from the identity provider during login or signup.

    Why this exists:
    The system can receive the same request flow for both returning users and
    first-time users. Because of that, the serializer has to decide whether the
    person already exists in our database and apply the right checks.

    Business rules:
    - Every request must include email, password, and role.
    - New users must also send confirm_password.
    - If confirm_password is sent, it must match password.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    # Returning users may already exist in the local database,
    # so confirm_password is only forced for first-time account creation.
    confirm_password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )
    role = serializers.CharField(required=True)

    def validate(self, data):
        """
        Apply signup/login validation based on whether the user already exists.

        Why this validation matters:
        The backend should not trust the client to know if someone is new or
        returning. This check keeps account creation safe by making sure a new
        user confirms their password before being accepted into the system.
        """
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        user_exists = User.objects.filter(email=email).exists()

        if not user_exists and not confirm_password:
            raise ValidationError({
                "confirm_password": "New users must confirm their password."
            })

        if confirm_password and password != confirm_password:
            raise ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Returns the logged-in user's profile details.

    Why this exists:
    The frontend often needs a safe summary of the current user after login,
    token verification, or page refresh. This serializer exposes identity and
    role-related fields without allowing the client to edit them directly here.

    Business logic:
    - Share only profile fields needed by the app.
    - Keep all fields read-only so this serializer is used for display, not
      profile updates.
    """

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'registration_number',
            'employee_id',
        ]
        read_only_fields = fields