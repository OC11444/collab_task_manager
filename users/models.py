#users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    # Define our specific college roles
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    # use modules for better modular scalable app-dont link other apps to other apps ---james
    # Specific fields for different roles
    registration_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_class_rep = models.BooleanField(default=False)

    # 🟢 Presence Heartbeat
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


class PendingUser(models.Model):
    # Store users awaiting verification before creating a full account
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=User.ROLE_CHOICES, default='student')
    hashed_password = models.CharField(max_length=255)
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - pending {self.role}"