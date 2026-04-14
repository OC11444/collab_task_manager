# users/urls.py
from django.urls import path
from .views import LoginSyncView

urlpatterns = [
    path('login/', LoginSyncView.as_view(), name='api-login'),
]