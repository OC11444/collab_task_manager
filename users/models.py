# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Define our specific college roles
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
#use modules for better modular scalable app-dont link other apps to other apps ---james
    # Specific fields for different roles
    registration_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_class_rep = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"