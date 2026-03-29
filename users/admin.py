from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# We create a custom layout based on the secure UserAdmin
class CustomUserAdmin(UserAdmin):
    # We take the default Django fields and ADD our custom "College Details" section
    fieldsets = UserAdmin.fieldsets + (
        ('College Details', {
            'fields': ('role', 'department', 'registration_number', 'employee_id', 'is_class_rep')
        }),
    )

# Register the User table using our new, upgraded layout
admin.site.register(User, CustomUserAdmin)