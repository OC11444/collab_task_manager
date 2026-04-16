from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PendingUser
from .serializers import IdPSyncSerializer
from .services import perform_login_sync, provision_user_from_legacy
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer # Ensure this is in your serializers.py


class LoginSyncView(APIView):
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
                return Response({
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token)
                    },
                    "role": user.role
                })

            return Response(
                {"message": "Verification email sent. Check terminal."},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class SignupView(APIView):
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
    def get(self, request, token):
        pending_user = get_object_or_404(PendingUser, verification_token=token)

        try:
            user = provision_user_from_legacy(
                email=pending_user.email,
                role=pending_user.role,
                hashed_password=pending_user.hashed_password,
            )

            pending_user.delete()

            return Response(
                {
                    "message": "Account verified successfully.",
                    "username": user.username,
                    "role": user.role,
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
    Returns the profile of the currently authenticated user.
    Requires a valid JWT token in the Authorization header.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Because of IsAuthenticated, request.user is already the logged-in User object
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)