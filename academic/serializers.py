from rest_framework import serializers
from .models import School, Department, Course, Unit, Enrollment

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    school_name = serializers.ReadOnlyField(source='school.name')

    class Meta:
        model = Department
        fields = ['id', 'name', 'school', 'school_name', 'description']

class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')

    class Meta:
        model = Course
        fields = ['id', 'name', 'course_code', 'department', 'department_name']

class UnitSerializer(serializers.ModelSerializer):
    course_name = serializers.ReadOnlyField(source='course.name')

    class Meta:
        model = Unit
        # Changed 'unit_code' to 'code' to match the updated Model and Tests
        fields = ['id', 'name', 'code', 'course', 'course_name']

class EnrollmentSerializer(serializers.ModelSerializer):
    student_username = serializers.ReadOnlyField(source='student.username')
    unit_name = serializers.ReadOnlyField(source='unit.name')

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_username', 'unit', 'unit_name', 'date_enrolled']

from .models import Task, TaskSubmission


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
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
            'unit_code',
            'members',
            'status',
            'time_left',
            'allow_late_submissions',
        ]
        read_only_fields = ['created_by', 'unit_code', 'members', 'status', 'time_left']

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
    is_late = serializers.ReadOnlyField()

    class Meta:
        model = TaskSubmission
        fields = [
            'id',
            'task',
            'student',
            'submission_link',
            'submitted_at',
            'is_late',
            'status',
            'grade',
            'feedback',
        ]
        read_only_fields = ['student', 'submitted_at', 'is_late', 'grade', 'feedback']

    def validate(self, data):
        request = self.context.get('request')
        task = data.get('task') or getattr(self.instance, 'task', None)

        if request is None or task is None:
            return data

        user = request.user

        if not user.enrollments.filter(unit=task.unit).exists():
            raise serializers.ValidationError(
                {"task": "You are not enrolled in the unit for this task."}
            )

        return data