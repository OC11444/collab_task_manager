#users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
#Define our specific college roles
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    role=models.CharField(max_length=10,choices=ROLE_CHOICES,default='student')


    #  Linking to the Academic app
    # Notice we use a string ('academic.Department') instead of a direct import.
    # This is a cool Django trick to prevent "circular import" crashes between files!very hectic
    department = models.ForeignKey('academic.Department', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='users')

    #  Specific fields for different roles
    registration_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    is_class_rep = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"




