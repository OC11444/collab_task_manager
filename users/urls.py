# users/urls.py
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