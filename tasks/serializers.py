from django.apps import apps
from rest_framework import serializers

from .models import Task, TaskSubmission


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    unit = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academic', 'Unit').objects.all()
    )
    unit_code = serializers.ReadOnlyField(source='unit.code')
    members = serializers.SerializerMethodField()
    status = serializers.CharField(required=False)
    comments = serializers.SerializerMethodField()
    time_left = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'due_date', 'priority',
            'created_by', 'unit', 'unit_code', 'members',
            'status', 'comments', 'time_left', 'allow_late_submissions',
        ]
        read_only_fields = ['created_by', 'unit_code', 'members', 'time_left', 'comments']

    def get_comments(self, obj):
        # Lazy import to maintain Modular Monolith boundaries
        from comments_notifications.selectors import get_comments_for_object
        from comments_notifications.serializers import CommentSerializer

        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []

        comments = get_comments_for_object(target_object=obj, user=request.user)
        return CommentSerializer(comments, many=True, context=self.context).data

    def validate_unit(self, value):
        request = self.context.get('request')
        if request and request.user and not request.user.is_staff:
            # Query the Enrollment model directly to avoid relationship attribute errors
            Enrollment = apps.get_model('academic', 'Enrollment')
            if not Enrollment.objects.filter(unit=value, student=request.user).exists():
                raise serializers.ValidationError("You are not enrolled in this unit.")
        return value

    def validate_status(self, value):
        valid_statuses = {
            TaskSubmission.STATUS_TO_DO,
            TaskSubmission.STATUS_IN_PROGRESS,
            TaskSubmission.STATUS_DONE,
        }
        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid status value.")
        return value

    def get_members(self, obj):
        # Get the model and query it directly to find students in this unit
        Enrollment = apps.get_model('academic', 'Enrollment')
        enrollments = Enrollment.objects.filter(unit=obj.unit)
        return [e.student.username for e in enrollments]

    def get_status(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return TaskSubmission.STATUS_TO_DO

        submission = obj.submissions.filter(student=request.user).first()
        return submission.status if submission else TaskSubmission.STATUS_TO_DO

    def get_time_left(self, obj):
        if not obj.due_date:
            return None

        from django.utils import timezone
        delta = obj.due_date - timezone.now()
        return max(int(delta.total_seconds()), 0)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['status'] = self.get_status(instance)
        return data

    def update(self, instance, validated_data):
        request = self.context.get('request')
        new_status = validated_data.pop('status', None)

        #  ARCHITECTURAL FIX: Allow all authenticated users to track personal progress
        if new_status is not None and request and request.user.is_authenticated:
            TaskSubmission.objects.update_or_create(
                task=instance,
                student=request.user,
                defaults={'status': new_status},
            )

        return super().update(instance, validated_data)


class TaskSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')
    task_title = serializers.ReadOnlyField(source='task.title')
    is_late = serializers.ReadOnlyField()

    class Meta:
        model = TaskSubmission
        fields = [
            'id', 'task', 'task_title', 'student', 'submission_link',
            'status', 'grade', 'feedback', 'submitted_at', 'is_late',
        ]
        read_only_fields = ['student', 'grade', 'feedback', 'submitted_at', 'is_late']