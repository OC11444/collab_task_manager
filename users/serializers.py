from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class IdPSyncSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    # confirm_password is optional because returning users won't need it
    confirm_password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    role = serializers.CharField(required=True)

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Logic check: If confirm_password is provided, it MUST match the password
        if confirm_password and password != confirm_password:
            raise ValidationError({"confirm_password": "Passwords do not match."})

        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer to return the current user's profile data.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'registration_number', 'employee_id']
        read_only_fields = fields