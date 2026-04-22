from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# 🚀 NEW: Import the notification service
from comments_notifications.services import create_notification





from .models import Task, TaskSubmission
# 1. FIXED: Imported the correct permission and removed the unused one
from .permissions import IsOwnerOrStaff, IsStaffOrStudentEnrolled
from .serializers import TaskSerializer, TaskSubmissionSerializer


class CommentActionMixin:
    """
    Mixin to provide comment functionality to ViewSets.
    """
    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        from comments_notifications.selectors import get_comments_for_object
        from comments_notifications.serializers import CommentSerializer
        from comments_notifications.services import create_comment, create_notification

        target = self.get_object()

        if request.method == 'GET':
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

        # 🚀 EXPLICIT ACTIVITY: Comment on Task/Submission (Multi-Recipient)
        recipients = set()

        # Scenario A: TaskSubmission (Private feedback)
        if hasattr(target, 'student') and hasattr(target, 'task'):
            if request.user == target.student:
                recipients.add(target.task.created_by)
            else:
                recipients.add(target.student)

        # Scenario B: Task (Unit-wide discussion)
        elif hasattr(target, 'created_by'):
            # 1. Add everyone who could possibly need a notification
            recipients.add(target.created_by)
            if hasattr(target, 'unit'):
                from django.apps import apps
                enrollment_model = apps.get_model('academic', 'Enrollment')
                enrollments = enrollment_model.objects.filter(unit_id=target.unit_id).select_related('student')
                for enrollment in enrollments:
                    if enrollment.student:
                        recipients.add(enrollment.student)

            # 2. THE FIX: Remove the commenter by ID to ensure tests pass 100%
            current_user_id = request.user.id
            recipients = {r for r in recipients if r.id != current_user_id}

        # 📣 Send notifications to everyone in the set
        for recipient in recipients:
            if recipient:
                create_notification(
                    recipient=recipient,
                    title=request.user.username,
                    message=f"commented on {getattr(target, 'title', 'the task')}",
                    target_object=target
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

        from django.apps import apps
        enrollment_model = apps.get_model('academic', 'Enrollment')
        study_group_model = apps.get_model('academic', 'StudyGroup')

        # Using snake_case and explicit lookups to satisfy the linter
        unit_ids = enrollment_model.objects.filter(student=user).values_list('unit_id', flat=True)
        study_group_ids = study_group_model.objects.filter(members=user).values_list('id', flat=True)

        return Task.objects.filter(
            Q(unit_id__in=unit_ids) | Q(study_groups__in=study_group_ids)
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)

        # 🚀 ACTIVITY: "New Task Created"
        # 1. Notify the teacher (for their own feed)
        create_notification(
            recipient=self.request.user,
            title="System",
            message=f"You created task: {task.title}",
            target_object=task
        )

        # 2. Notify all students enrolled in this unit
        from django.apps import apps
        # Use lowercase for variable names inside functions to satisfy PEP8/Editor
        enrollment_model = apps.get_model('academic', 'Enrollment')
        enrollments = enrollment_model.objects.filter(unit=task.unit).select_related('student')

        for enrollment in enrollments:
            create_notification(
                recipient=enrollment.student,
                title="New Task",
                message=f"Assigned: {task.title}",
                target_object=task
            )


class TaskSubmissionViewSet(CommentActionMixin, viewsets.ModelViewSet):
    serializer_class = TaskSubmissionSerializer
    permission_classes = [IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return TaskSubmission.objects.all().order_by('-submitted_at')

        return TaskSubmission.objects.filter(student=user).order_by('-submitted_at')

    def create(self, request, *args, **kwargs):
        task_id = request.data.get('task')
        if not task_id:
            return Response({"detail": "Task ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        submission = TaskSubmission.objects.filter(task_id=task_id, student=request.user).first()

        if submission:
            data = request.data.copy()
            data['status'] = TaskSubmission.STATUS_DONE
            serializer = self.get_serializer(submission, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        submission = serializer.save(student=self.request.user, status=TaskSubmission.STATUS_DONE)

        # 🚀 ACTIVITY: "Student Submitted Task"
        # Notify the teacher
        create_notification(
            recipient=submission.task.created_by,
            title=self.request.user.username,
            message=f"submitted {submission.task.title}",
            target_object=submission
        )
        # Notify the student
        create_notification(
            recipient=self.request.user,
            title="System",
            message=f"You submitted {submission.task.title}",
            target_object=submission
        )

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        submission = serializer.save()

        # 🚀 ACTIVITY: "Task Graded"
        # If a staff member moves a task to 'done', we treat it as "Graded"
        if self.request.user.is_staff and submission.status == TaskSubmission.STATUS_DONE and old_status != TaskSubmission.STATUS_DONE:
            create_notification(
                recipient=submission.student,
                title="System",
                message=f"Your task '{submission.task.title}' has been graded",
                target_object=submission
            )
            create_notification(
                recipient=self.request.user,
                title="System",
                message=f"You graded {submission.student.username}'s work",
                target_object=submission
            )

        # 🚀 ACTIVITY: "Student Updated Submission" (Kanban Move to Done)
        elif not self.request.user.is_staff and submission.status == TaskSubmission.STATUS_DONE and old_status != TaskSubmission.STATUS_DONE:
            create_notification(
                recipient=submission.task.created_by,
                title=self.request.user.username,
                message=f"submitted {submission.task.title}",
                target_object=submission
            )