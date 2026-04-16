# comments_notifications/views.py
from typing import Any, Type
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.apps import apps
from django.db.models import Model

from .serializers import CommentSerializer
from .selectors import get_comments_for_object
from .services import create_comment
from .models import Comment

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

        serializer = CommentSerializer(new_comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TaskCommentAPIView(BaseCommentAPIView):
    model_lookup = 'tasks.Task'

class TaskSubmissionCommentAPIView(BaseCommentAPIView):
    model_lookup = 'tasks.TaskSubmission'