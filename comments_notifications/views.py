from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Comment, Notification
from .serializers import CommentSerializer, NotificationSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for comments.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only comments related to tasks assigned to the current user
        return Comment.objects.filter(task__assigned_to=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the author to the logged-in user
        comment = serializer.save(author=self.request.user)

        # 🔥 Create notification when comment is added
        task = getattr(comment, 'task', None)

        if task.assigned_to:
            Notification.objects.create(
                recipient=task.assigned_to,
                task=task,
                message=f"New comment on your task: {task.title}",
                notification_type='comment'
            )


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Handles notifications for users.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Each user sees ONLY their notifications
        return Notification.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign recipient
        serializer.save(recipient=self.request.user)