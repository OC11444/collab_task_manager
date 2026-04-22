# comments_notifications/urls.py
from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationReadView,
)

urlpatterns = [
    # Notifications
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', MarkNotificationReadView.as_view(), name='notification-detail'),
]