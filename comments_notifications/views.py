from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.apps import apps

from .serializers import CommentSerializer
from .selectors import get_comments_for_object
from .services import create_comment
from .models import Comment


class TaskCommentAPIView(APIView):
    """
    Handles fetching and creating comments specifically for Tasks.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_task_object(self, task_id):
        # Modular Monolith Trick: Dynamically load the Task model
        # so we don't hard-import from the tasks app!
        Task = apps.get_model('tasks', 'Task')
        return get_object_or_404(Task, id=task_id)

    def get(self, request, task_id):
        task = self.get_task_object(task_id)

        # Use your Selector!
        comments = get_comments_for_object(target_object=task, user=request.user)

        # Pass the request context so the serializer can enforce RBAC on replies
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, task_id):
        task = self.get_task_object(task_id)

        content = request.data.get('content')
        parent_id = request.data.get('parent')

        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)

        # Use your Service!
        new_comment = create_comment(
            author=request.user,
            content=content,
            target_object=task,
            parent=parent_comment
        )

        serializer = CommentSerializer(new_comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
