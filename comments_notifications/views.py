# comments_notifications/views.py
from typing import Any, Type
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.apps import apps
from django.db.models import Model

from .serializers import CommentSerializer, NotificationSerializer
from .selectors import get_comments_for_object
from .services import create_comment, create_notification #  Added create_notification
from .models import Comment, Notification

class BaseCommentAPIView(APIView):
    """
    Base class to handle common logic for comments on different models.
    """
    permission_classes = [permissions.IsAuthenticated]
    model_lookup: str = "" # Defined in subclasses

    def get_target_object(self, pk: int) -> Model:
        app_label, model_name = self.model_lookup.split('.')
        # Use lowercase 'model_class' to satisfy PEP8
        # Type hint Type[Model] helps the editor understand get_object_or_404 usage
        model_class: Any = apps.get_model(app_label, model_name)
        return get_object_or_404(model_class, id=pk)

    def get(self, request, pk):
        target = self.get_target_object(pk)
        comments = get_comments_for_object(target_object=target, user=request.user)
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, pk):
        target = self.get_target_object(pk)
        content = request.data.get('content')
        parent_id = request.data.get('parent')

        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)

        new_comment = create_comment(
            author=request.user,
            content=content,
            target_object=target,
            parent=parent_comment
        )

        # 🚀 EXPLICIT ACTIVITY LOGGING
        # Identify who should receive the notification
        recipient = None

        # Scenario A: Comment on a TaskSubmission (Common for Grading/Feedback)
        if hasattr(target, 'student') and hasattr(target, 'task'):
            # If the lecturer comments, notify the student. If student comments, notify the lecturer.
            recipient = target.student if request.user != target.student else target.task.created_by

        # Scenario B: Comment on a Task (General discussion)
        elif hasattr(target, 'created_by'):
            # Notify the creator of the task if someone else comments
            if request.user != target.created_by:
                recipient = target.created_by

        if recipient:
            create_notification(
                recipient=recipient,
                title=request.user.username,
                message=f"commented on {getattr(target, 'title', 'your submission')}",
                target_object=target
            )

        serializer = CommentSerializer(new_comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TaskCommentAPIView(BaseCommentAPIView):
    model_lookup = 'tasks.Task'

class TaskSubmissionCommentAPIView(BaseCommentAPIView):
    model_lookup = 'tasks.TaskSubmission'

class NotificationListView(APIView):
    """
    Returns all notifications for the logged-in user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch notifications for this user, newest first
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class MarkNotificationReadView(APIView):
    """
    Sets a specific notification status to 'read'.
    """
    permission_classes = [permissions.IsAuthenticated]

    # Changed from post to patch to match the frontend axios request
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({"status": "success"})
