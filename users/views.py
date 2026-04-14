import csv
import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import IdPSyncSerializer

User = get_user_model()


class LoginSyncView(APIView):
    permission_classes = [AllowAny]

    def get_tokens_for_user(self, user):
        """Helper to generate JWT tokens manually"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def post(self, request):
        # 1. Validate the basic input format
        serializer = IdPSyncSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            role_from_frontend = serializer.validated_data['role']
            confirm_password = serializer.validated_data.get('confirm_password')

            # 2. Locate and search the CSV lookup table
            csv_path = os.path.join(settings.BASE_DIR, 'users', 'data', 'university_db.csv')
            user_info = None

            try:
                with open(csv_path, mode='r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['email'] == email:
                            user_info = row
                            break
            except FileNotFoundError:
                return Response(
                    {"error": "Central database not found."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 3. Decision Logic
            if user_info:
                # Security Check: Does the selected toggle match the CSV record?
                if user_info['role'] != role_from_frontend:
                    return Response(
                        {"error": "Role mismatch. Please select the correct role."},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # Check if they already have an account in our local DB
                user = User.objects.filter(email=email).first()

                if user:
                    # PATH A: Returning User - Verify existing password
                    if user.check_password(password):
                        tokens = self.get_tokens_for_user(user)
                        return Response({
                            "message": f"Welcome back, {user.username}!",
                            "tokens": tokens,
                            "role": user.role
                        }, status=status.HTTP_200_OK)
                    return Response({"error": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)

                else:
                    # PATH B: New User - Create account from CSV data
                    if not confirm_password:
                        return Response(
                            {"error": "First-time login requires password confirmation."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Create the local record
                    new_user = User.objects.create(
                        username=user_info['username'],
                        email=email,
                        role=user_info['role'],
                        registration_number=user_info.get('registration_number')
                    )
                    # Securely hash the password
                    new_user.set_password(password)
                    new_user.save()

                    tokens = self.get_tokens_for_user(new_user)
                    return Response({
                        "message": f"Account created! Welcome, {new_user.username}.",
                        "tokens": tokens,
                        "role": new_user.role
                    }, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Email not found in university records."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)