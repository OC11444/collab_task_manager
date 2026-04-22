from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from users.models import PendingUser, User
from users.selectors import get_university_record
from django.conf import settings
from django.contrib.auth.hashers import make_password


def perform_login_sync(email, role, password, request, *, confirm_password=None):
    """
    Orchestrates the identity flow. Returns: (User, None) or (None, PendingUser).
    """
    university_record = get_university_record(email)
    if not university_record:
        raise ValidationError("Email not found in university records.")

    # 🛡️ Smart Role Checking
    csv_role = str(university_record.get('role', '')).strip().lower()
    incoming_role = str(role).strip().lower()
    staff_aliases = ['staff', 'lecturer', 'teacher']

    is_valid_role = False
    if csv_role == incoming_role:
        is_valid_role = True
    elif csv_role in staff_aliases and incoming_role in staff_aliases:
        is_valid_role = True

    if not is_valid_role:
        # SECURE: Generic message for the user
        raise ValidationError("Authentication failed. Please ensure you are using the correct login portal.")

    user = User.objects.filter(email=email).first()

    if user:
        if not user.check_password(password):
            raise ValidationError("Invalid password.")
        return user, None
    else:
        if not confirm_password:
            raise ValidationError("First-time login requires password confirmation.")
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")

        pending_user = request_user_registration(email, role, password)
        send_verification_email(pending_user, request)
        return None, pending_user


def provision_user_from_legacy(email, role, hashed_password):
    """Converts a verified PendingUser into a real User using Legacy CSV data."""
    legacy_user = get_university_record(email)
    if not legacy_user:
        raise ValueError("Legacy record not found for this email.")

    # 🛡️ ARCHITECTURAL FIX: Define Django's internal flags based on our business roles
    is_staff_flag = (role in ['staff', 'admin'])
    is_superuser_flag = (role == 'admin')

    user = User(
        username=legacy_user["username"],
        email=email,
        role=role,
        is_staff=is_staff_flag,        # Added this
        is_superuser=is_superuser_flag # Added this
    )

    # Map legacy ID based on role
    if role == "student":
        user.registration_number = legacy_user.get("registration_number")
    else:
        user.employee_id = legacy_user.get("registration_number")

    user.password = hashed_password  # Already hashed in PendingUser
    user.save()
    return user


def request_user_registration(email, role, password):
    """Creates or updates a PendingUser record before verification."""
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
    """Sends the verification link to the terminal/email."""
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
    # Also print to terminal for easy dev testing
    print(f"\n--- VERIFICATION LINK ---")
    print(f"To: {pending_user.email}")
    print(f"Link: {verify_link}")
    print(f"---------------------------\n")