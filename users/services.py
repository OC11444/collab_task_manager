"""
Users service layer for authentication and first-time account setup.

Author: Mich omolo
"""

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from users.models import PendingUser, User
from users.selectors import get_university_record
from django.conf import settings
from django.contrib.auth.hashers import make_password


def perform_login_sync(email, role, password, request, *, confirm_password=None):
    """
    Handle login and first-time registration using the university record as
    the source of truth.

    Why this exists:
    This function keeps the login flow in one place so the app can decide
    whether a person should be logged in as an existing user or moved into
    the first-time verification flow. It also checks that the selected portal
    matches the role stored in university records, which helps stop people
    from entering through the wrong login path.

    Business logic:
    - Look up the email in university records before doing anything else.
    - Compare the incoming role with the university role.
    - Treat staff-like role names as equivalent so lecturer, teacher, and
      staff can still pass role validation when they mean the same internal
      category.
    - If a real user already exists, validate the password and log them in.
    - If no real user exists yet, require password confirmation and create
      a pending account that must be verified first.

    Returns:
        tuple:
            - (user, None) for an existing verified account
            - (None, pending_user) for a first-time account waiting verification
    """
    university_record = get_university_record(email)
    if not university_record:
        raise ValidationError("Email not found in university records.")

    # Read the role from the university source and normalise values so the
    # app compares meaning, not formatting.
    csv_role = str(university_record.get("role", "")).strip().lower()
    incoming_role = str(role).strip().lower()
    staff_aliases = ["staff", "lecturer", "teacher"]

    is_valid_role = False
    if csv_role == incoming_role:
        is_valid_role = True
    elif csv_role in staff_aliases and incoming_role in staff_aliases:
        is_valid_role = True

    if not is_valid_role:
        # Keep the response generic so the system does not leak role details.
        raise ValidationError(
            "Authentication failed. Please ensure you are using the correct login portal."
        )

    user = User.objects.filter(email=email).first()

    if user:
        # Existing users should already have completed verification, so only
        # the password check is needed here.
        if not user.check_password(password):
            raise ValidationError("Invalid password.")
        return user, None

    # No real user exists yet, so this is treated as first-time setup.
    if not confirm_password:
        raise ValidationError("First-time login requires password confirmation.")
    if password != confirm_password:
        raise ValidationError("Passwords do not match.")

    pending_user = request_user_registration(email, role, password)
    send_verification_email(pending_user, request)
    return None, pending_user


def provision_user_from_legacy(email, role, hashed_password):
    """
    Create a real User from a verified pending account using university data.

    Why this exists:
    The system does not allow direct account creation from user input alone.
    It builds the real account from trusted university records after email
    verification. This helps keep names, usernames, and institutional IDs
    aligned with official data.

    Business logic:
    - Pull the university record again to populate the final User object.
    - Set Django permission flags from business roles.
    - Ensure staff status is synced with roles so admin and staff users can
      access staff-only parts of the system correctly.
    - Store registration numbers for students and employee IDs for non-students.
    - Reuse the already-hashed password from PendingUser instead of hashing again.

    Args:
        email (str): Verified email address.
        role (str): Business role selected for the account.
        hashed_password (str): Password hash stored on PendingUser.

    Returns:
        User: Saved user account ready for authentication.
    """
    legacy_user = get_university_record(email)
    if not legacy_user:
        raise ValueError("Legacy record not found for this email.")

    # Map business roles to Django auth flags so platform permissions match
    # the kind of account being created.
    is_staff_flag = role in ["staff", "admin"]
    is_superuser_flag = role == "admin"

    user = User(
        username=legacy_user["username"],
        email=email,
        role=role,
        is_staff=is_staff_flag,
        is_superuser=is_superuser_flag,
    )

    # The university source stores one identifier field, but this project
    # saves it differently depending on account type.
    if role == "student":
        user.registration_number = legacy_user.get("registration_number")
    else:
        user.employee_id = legacy_user.get("registration_number")

    user.password = hashed_password
    user.save()
    return user


def request_user_registration(email, role, password):
    """
    Create or refresh a PendingUser record for first-time account setup.

    Why this exists:
    New users should not become full accounts immediately. The pending record
    acts as a holding area until email verification is completed. This lowers
    the chance of unverified accounts being treated as real users.

    Business logic:
    - Stop the flow if the email already belongs to a real registered user.
    - Create a pending account if it does not exist.
    - Update the existing pending account if the user restarts registration.
    - Always store a hashed password, never plain text.

    Args:
        email (str): Email being registered.
        role (str): Selected business role.
        password (str): Raw password from the first-time login form.

    Returns:
        PendingUser: Pending registration record waiting for verification.
    """
    if User.objects.filter(email=email).exists():
        raise ValidationError("User already registered")

    pending_user, _ = PendingUser.objects.update_or_create(
        email=email,
        defaults={
            "role": role,
            "hashed_password": make_password(password),
        },
    )
    return pending_user


def send_verification_email(pending_user, request):
    """
    Send the account verification link for a pending registration.

    Why this exists:
    A first-time user must prove they control the email address before the
    system creates a real account. This step closes the loop between pending
    registration and verified user creation.

    Business logic:
    - Build a frontend verification URL using the pending user's token.
    - Send the link to the pending email address.
    - Print the same link in development so testing can continue even when
      email delivery is not the main focus.

    Args:
        pending_user (PendingUser): Pending account waiting for verification.
        request: Incoming HTTP request context.
    """
    token = str(pending_user.verification_token)
    frontend_url = settings.FRONTEND_URL
    verify_link = f"{frontend_url}/#/verify/{token}"

    text_message = f"Welcome! Click here to verify your account: {verify_link}"

    send_mail(
        subject="Verify your email - Collab Task Manager",
        message=text_message,
        from_email=None,
        recipient_list=[pending_user.email],
    )

    # Development helper: makes manual testing easier when checking new signups.
    print("\n--- VERIFICATION LINK ---")
    print(f"To: {pending_user.email}")
    print(f"Link: {verify_link}")
    print("---------------------------\n")