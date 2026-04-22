"""
Users admin module for the Django Modular Monolith project.

Author: Mich omolo
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    """
    Custom admin setup for the User model.

    Why this exists:
    The project uses a custom user model with university-specific fields.
    Django's default admin only covers the normal authentication details,
    so this admin class extends that layout to include academic and staff
    identity data in one place.

    Business reason:
    Admin users need to manage both login details and institution details
    from the same screen. This makes it easier to create and update users
    without switching between different tools or storing student and staff
    information somewhere else.
    """

    fieldsets = UserAdmin.fieldsets + (
        (
            "College Details",
            {
                "fields": (
                    "role",
                    "department",
                    "registration_number",
                    "employee_id",
                    "is_class_rep",
                )
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)