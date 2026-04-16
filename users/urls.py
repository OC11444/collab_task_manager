# users/urls.py
from django.urls import path

from .views import LoginSyncView, SignupView, VerifyEmailView  # <--- Use the Class names

from .views import LoginSyncView, SignupView, VerifyEmailView, UserMeView

urlpatterns = [
    path('login/', LoginSyncView.as_view(), name='api-login'),

    # Use .as_view() for all class-based views
    path('signup/', SignupView.as_view(), name='api-signup'),
    path('verify/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),

    path('me/', UserMeView.as_view(), name='user-me'),
]