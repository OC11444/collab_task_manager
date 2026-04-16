from rest_framework import generics, views  # Added views
from rest_framework.response import Response  # Added Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.apps import apps  # Safer for Modular Monolith cross-app access

from .serializers import UnitDashboardSerializer
from .selectors import get_latest_unit_snapshots_for_lecturer


class LecturerDashboardView(generics.ListAPIView):
    serializer_class = UnitDashboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_latest_unit_snapshots_for_lecturer(self.request.user)


class TaskSummaryReportView(views.APIView):
    """
    New View: Pulls metrics for a specific task.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        # Dynamically load models to avoid circular imports between apps
        Task = apps.get_model('tasks', 'Task')
        TaskSubmission = apps.get_model('tasks', 'TaskSubmission')
        Enrollment = apps.get_model('academic', 'Enrollment')

        task = get_object_or_404(Task, id=task_id)

        # Aggregate the data
        total_enrolled = Enrollment.objects.filter(unit=task.unit).count()
        total_submitted = TaskSubmission.objects.filter(task=task).count()

        # Completion Rate Math
        rate = (total_submitted / total_enrolled * 100) if total_enrolled > 0 else 0

        return Response({
            "task_id": task.id,
            "title": task.title,
            "stats": {
                "total_students": total_enrolled,
                "submissions": total_submitted,
                "completion_rate": f"{round(rate, 2)}%"
            }
        })