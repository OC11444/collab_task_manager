from rest_framework import serializers

from .models import Task, TaskSubmission


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    unit = serializers.PrimaryKeyRelatedField(queryset=Task._meta.get_field('unit').remote_field.model.objects.all())
    unit_code = serializers.ReadOnlyField(source='unit.code')
    members = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    time_left = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'due_date',
            'priority',
            'created_by',
            'unit',
            'unit_code',
            'members',
            'status',
            'time_left',
            'allow_late_submissions',
        ]
        read_only_fields = ['created_by', 'unit_code', 'members','time_left']

    def validate_unit(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")

        lecturer_field = value._meta.get_field('lecturer')
        lecturer_id = getattr(value, lecturer_field.attname, None)

        if lecturer_id != user.id:
            raise serializers.ValidationError(
                "You are not authorized to create tasks for this unit."
            )

        return value

    def get_members(self, obj):
        members = obj.study_groups.values_list('members__username', flat=True).distinct()
        return list(members)

    def get_status(self, obj):
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return 'To Do'

        submission = obj.submissions.filter(student=request.user).first()

        if not submission:
            return 'To Do'

        status_map = {
            'to_do': 'To Do',
            'in_progress': 'In Progress',
            'done': 'Done',
        }
        return status_map.get(submission.status, 'To Do')

    def get_time_left(self, obj):
        from django.utils import timezone

        now = timezone.now()
        if obj.due_date > now:
            diff = obj.due_date - now
            if diff.days > 0:
                return f"{diff.days}d left"
            hours = diff.seconds // 3600
            return f"{hours}h left"
        return "Expired"


class TaskSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')
    task_title = serializers.ReadOnlyField(source='task.title')
    is_late = serializers.ReadOnlyField()

    class Meta:
        model = TaskSubmission
        fields = [
            'id',
            'task',
            'task_title',
            'student',
            'submission_link',
            'status',
            'grade',
            'feedback',
            'submitted_at',
            'is_late',

        ]
        read_only_fields = ['student', 'grade', 'feedback', 'submitted_at', 'is_late']

    def validate(self, data):
        request = self.context.get('request')
        instance = getattr(self, 'instance', None)
        task = data.get('task') or (instance.task if instance else None)

        if not request or not task:
            return data

        submission_link = data.get(
            'submission_link',
            instance.submission_link if instance else None,
        )
        status = data.get('status', instance.status if instance else None)

        if status == 'done' and not submission_link:
            raise serializers.ValidationError(
                {"submission_link": "You cannot mark a task as Done without a submission link."}
            )

        user = request.user
        is_enrolled = user.enrollments.filter(unit=task.unit).exists()
        is_in_group = task.study_groups.filter(members=user).exists()

        if not (is_enrolled or is_in_group):
            raise serializers.ValidationError(
                {"task": "You are not authorized to submit for this task."}
            )

        return data