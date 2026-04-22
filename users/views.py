"""
Module: users
Author: Mich omolo

Handles the core business logic for user accounts. This includes processing logins, managing the two-step email verification for new signups, and keeping track of user presence for the live dashboard.
"""
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PendingUser, User  # 👈 Added User here!
from .serializers import IdPSyncSerializer
from .services import perform_login_sync, provision_user_from_legacy
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer


class LoginSyncView(APIView):
    """
        Process user login requests. If the user is valid, we hand back their JWT access tokens and role so the frontend knows what dashboard to load for them.
        """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = IdPSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, pending_user = perform_login_sync(
                request=request,
                **serializer.validated_data
            )

            if user:
                refresh = RefreshToken.for_user(user)
                # Include basic user info in response for frontend
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "role": user.role,
                    "user": {
                        "username": user.username,
                        "email": user.email
                    }
                })

            return Response(
                {"message": "Verification email sent. Check terminal."},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            # Keep this for your eyes only (the terminal)
            print(f"DEBUG ERROR: {str(e)}")

            # Send a safe, generic message to the frontend/user
            return Response(
                {"error": f"The exact bug is: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class SignupView(APIView):
    """
        Starts the registration process. We do not create the full user account right away. Instead, we save them as a pending user and trigger an email with a verification link to prove they own the email address.
        """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        role = request.data.get("role")
        password = request.data.get("password")

        try:
            from .services import request_user_registration, send_verification_email

            pending_user = request_user_registration(
                email=email,
                role=role,
                password=password
            )
            send_verification_email(pending_user, request)

            return Response(
                {"message": "Registration started. Check terminal for the verification link."},
                status=status.HTTP_201_CREATED
            )
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )


class VerifyEmailView(APIView):
    """
        Catches the verification link from the user's email. Once we confirm the token is valid, we move them from a pending state to a fully provisioned system user and log them in automatically.
        """
    permission_classes = [AllowAny]

    def get(self, request, token):
        pending_user = get_object_or_404(PendingUser, verification_token=token)

        try:
            user = provision_user_from_legacy(
                email=pending_user.email,
                role=pending_user.role,
                hashed_password=pending_user.hashed_password,
            )

            pending_user.delete()

            # Generate the JWT tokens for the newly verified user
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Account verified successfully.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "role": user.role,
                    "user": {
                        "username": user.username,
                        "email": user.email
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Verification failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserMeView(APIView):
    """
        A simple endpoint for the frontend to ask 'who am I?'. It returns the profile details of whoever holds the current active JWT token.
        """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamPresenceView(APIView):
    """
        Acts as a heartbeat for the live dashboard. When a user pings this, we update their last seen timestamp. We then return a list of everyone who has been active in the last 5 minutes so the frontend can show the online status indicators.
        """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Update my heartbeat
        request.user.last_seen = timezone.now()
        request.user.save(update_fields=['last_seen'])

        # 2. Determine who is online (active in the last 5 minutes)
        five_mins_ago = timezone.now() - timedelta(minutes=5)
        all_users = User.objects.all()

        # 3. Format exactly how the React frontend expects it
        members_data = []
        for u in all_users:
            is_online = bool(u.last_seen and u.last_seen >= five_mins_ago)
            members_data.append({
                "id": str(u.id),
                "name": u.username or u.email.split('@')[0],
                "initials": (u.username[:2] if u.username else u.email[:2]).upper(),
                "color": "#3b82f6" if u.role in ["staff", "teacher"] else "#10b981", # Blue for staff, Green for students
                "isOnline": is_online
            })

        return Response(members_data, status=status.HTTP_200_OK)