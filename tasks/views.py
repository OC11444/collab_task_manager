from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from academic.selectors import (
    get_user_enrolled_unit_ids,
    get_user_study_group_ids,
)
from comments_notifications.selectors import get_comments_for_object
from comments_notifications.serializers import CommentSerializer
from comments_notifications.services import create_comment

from .models import Task, TaskSubmission
# 1. FIXED: Imported the correct permission and removed the unused one
from .permissions import IsOwnerOrStaff, IsStaffOrStudentEnrolled
from .serializers import TaskSerializer, TaskSubmissionSerializer


class CommentActionMixin:
    """
    Mixin to share comment logic between Task and Submission ViewSets
    to fix the 'Duplicated code fragment' warning.
    """
    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None): # pk is required by DRF action signature
        target = self.get_object()

        if request.method == 'GET':
            # 2. FIXED: Passed request.user to satisfy 'Parameter user unfilled'
            comments = get_comments_for_object(target_object=target, user=request.user)
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = create_comment(
            author=request.user,
            content=serializer.validated_data['content'],
            target_object=target,
            parent=serializer.validated_data.get('parent'),
        )

        response_serializer = CommentSerializer(comment, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TaskViewSet(CommentActionMixin, viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsStaffOrStudentEnrolled]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Task.objects.all().order_by('-created_at')

        unit_ids = get_user_enrolled_unit_ids(user)
        study_group_ids = get_user_study_group_ids(user)

        return Task.objects.filter(
            Q(unit_id__in=unit_ids) | Q(study_groups__in=study_group_ids)
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskSubmissionViewSet(CommentActionMixin, viewsets.ModelViewSet):
    serializer_class = TaskSubmissionSerializer
    permission_classes = [IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return TaskSubmission.objects.all().order_by('-submitted_at')

        return TaskSubmission.objects.filter(student=user).order_by('-submitted_at')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)