from datetime import timedelta

from django.apps import apps
from django.db.models import F
from django.utils import timezone

from .models import UnitPerformanceSnapshot


class ReportService:
    @classmethod
    def calculate_unit_metrics(cls, unit_id):
        Enrollment = apps.get_model('academic', 'Enrollment')
        Task = apps.get_model('tasks', 'Task')
        TaskSubmission = apps.get_model('tasks', 'TaskSubmission')

        now = timezone.now()
        feedback_deadline = now - timedelta(days=7)

        student_count = Enrollment.objects.filter(unit_id=unit_id).count()
        task_count = Task.objects.filter(unit_id=unit_id).count()
        expected_total = student_count * task_count

        actual_submissions = TaskSubmission.objects.filter(task__unit_id=unit_id)
        actual_count = actual_submissions.count()

        sub_rate = (actual_count / expected_total * 100) if expected_total > 0 else 0
        on_time_count = actual_submissions.filter(
            submitted_at__lte=F('task__due_date')
        ).count()
        on_time_ratio = (on_time_count / actual_count * 100) if actual_count > 0 else 0

        pending_reviews = actual_submissions.filter(grade__isnull=True).count()
        overdue_feedback = actual_submissions.filter(
            grade__isnull=True,
            submitted_at__lt=feedback_deadline,
        ).count()

        return {
            'submission_rate': round(sub_rate, 2),
            'on_time_ratio': round(on_time_ratio, 2),
            'pending_reviews': pending_reviews,
            'overdue_feedback': overdue_feedback,
        }

    @classmethod
    def create_unit_snapshot(cls, unit_id, lecturer_id, snapshot_type='progress'):
        """Persistence Layer: Saves the calculated metrics to the DB."""
        metrics = cls.calculate_unit_metrics(unit_id)

        return UnitPerformanceSnapshot.objects.create(
            unit_id=unit_id,
            lecturer_id=lecturer_id,
            submission_rate=metrics['submission_rate'],
            on_time_ratio=metrics['on_time_ratio'],
            pending_reviews=metrics['pending_reviews'],
            overdue_feedback=metrics['overdue_feedback'],
            snapshot_type=snapshot_type,
        )