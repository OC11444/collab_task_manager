# users/urls.py
"""
Module: users
Author: Mich omolo

Maps the URL endpoints for our authentication system. We route login, signup, email verification, and the heartbeat endpoint that tracks who is currently online in the system.
"""
from django.urls import path
from .views import LoginSyncView, SignupView, VerifyEmailView, UserMeView, TeamPresenceView, TeamPresenceView, TeamPresenceView

urlpatterns = [
    # Auth endpoints
    path('login/', LoginSyncView.as_view(), name='api-login'),
    path('signup/', SignupView.as_view(), name='api-signup'),

    # Verification & Profile
    path('verify/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('me/', UserMeView.as_view(), name='user-me'),

    # 🟢 Presence Heartbeat
    path('presence/', TeamPresenceView.as_view(), name='team-presence'),
]