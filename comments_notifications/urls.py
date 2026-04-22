"""
Module: comments_notifications
Author: OC11444

Maps the API endpoints for retrieving alerts and marking them as read.
"""
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