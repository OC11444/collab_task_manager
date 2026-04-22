"""
Users module models.

Author: Mich omolo

This file defines the user records used by the system.

Business purpose:
- Keep one central user model for authentication and role-based access.
- Store extra identity fields needed in a university setup, like
  registration numbers for students and employee IDs for staff.
- Support account verification by holding unverified users separately
  before a full account is created.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """
    Main user model for the platform.

    Why this exists:
    The project needs one shared user table that works across modules.
    Django already gives login, password handling, and permissions
    through `AbstractUser`, so this model extends that base and adds
    university-specific data.

    Business logic:
    - `role` separates students, staff, and admins so the system can
      decide what each person is allowed to do.
    - `registration_number` is only relevant for student accounts and
      helps match a user to academic records.
    - `employee_id` is only relevant for staff or admin accounts and
      supports staff identification in teaching and reporting workflows.
    - `is_class_rep` marks students with student leadership duties.
      This makes it easy to give class representatives extra actions
      without creating a separate user type.
    - `last_seen` stores the latest known activity time. This can be
      used for presence tracking, support, and simple activity checks.
    """

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        help_text="High-level account role used for access decisions in the platform.",
    )
    registration_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Student registration number, used when the account belongs to a student.",
    )
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Staff or admin employee identifier for institutional tracking.",
    )
    is_class_rep = models.BooleanField(
        default=False,
        help_text="Marks whether a student serves as a class representative.",
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Latest recorded activity timestamp for simple presence tracking.",
    )

    def __str__(self):
        """
        Return a readable label for admin pages and logs.

        Why this format:
        Showing both username and role makes it easier to tell users apart
        quickly, especially when the same system is used by students,
        lecturers, and admins.
        """
        return f"{self.username} - {self.get_role_display()}"


class PendingUser(models.Model):
    """
    Temporary record for users who have started signup but are not yet verified.

    Why this exists:
    The system should not create a full account immediately before email
    or onboarding checks are complete. Keeping pending users separate
    avoids mixing unverified accounts with active users.

    Business logic:
    - `email` identifies the pending signup and prevents duplicate
      verification requests for the same address.
    - `role` captures the expected account type early so verification
      and account creation follow the correct path.
    - `hashed_password` stores the prepared password safely until the
      account is confirmed and promoted into the main user table.
    - `verification_token` gives each pending signup a unique value for
      verification links.
    - `created_at` helps with expiry checks, cleanup, and audit needs.
    """

    email = models.EmailField(
        unique=True,
        help_text="Email address waiting for verification before account creation.",
    )
    role = models.CharField(
        max_length=10,
        choices=User.ROLE_CHOICES,
        default='student',
        help_text="Intended role for the account being verified.",
    )
    hashed_password = models.CharField(
        max_length=255,
        help_text="Hashed password stored temporarily until verification is complete.",
    )
    verification_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Unique token used to verify and activate the pending account.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp used for tracking age, expiry, and cleanup of pending signups.",
    )

    def __str__(self):
        """
        Return a readable label for pending account records.

        Why this format:
        Admins and developers can quickly see which email is waiting
        for verification and which role that signup requested.
        """
        return f"{self.email} - pending {self.role}"