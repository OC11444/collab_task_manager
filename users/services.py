from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from users.models import PendingUser, User
from users.selectors import get_university_record


def perform_login_sync(email, role, password, request, *, confirm_password=None):
    """
    Orchestrates the entire identity flow.
    Returns: (User, None) if returning, (None, PendingUser) if new.
    """
    university_record = get_university_record(email)
    if not university_record:
        raise ValidationError("Email not found in university records.")

    if university_record['role'] != role:
        raise ValidationError("Role mismatch. Please select the correct role.")

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
    """
    Converts a verified PendingUser into a real User in the database.
    This is called when the user clicks the email link.
    """
    legacy_user = get_university_record(email)
    if not legacy_user:
        raise ValueError("Legacy record disappeared.")

    user = User(
        username=legacy_user["username"],
        email=email,
        role=role,
    )

    # Map CSV fields to correct Model fields based on role
    if role == "student":
        user.registration_number = legacy_user.get("registration_number")
    else:
        user.employee_id = legacy_user.get("registration_number")

    user.password = hashed_password
    user.save()
    return user


def request_user_registration(email, role, password):
    """Creates/Updates the temporary verification record."""
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
    """Generates the UUID link and sends it via the configured backend."""
    path = reverse("verify-email", kwargs={"token": str(pending_user.verification_token)})
    url = request.build_absolute_uri(path)

    send_mail(
        subject="Verify your email",
        message=f"Verify here: {url}",
        from_email=None,
        recipient_list=[pending_user.email],
    )