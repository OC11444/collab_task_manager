from django.urls import path
from .views import LecturerDashboardView, TaskSummaryReportView,GlobalUnitReportView # Added TaskSummaryReportView

urlpatterns = [
    path('dashboard/lecturer/', LecturerDashboardView.as_view(), name='lecturer-dashboard'),

    # New Path: Matches your curl command exactly
    path('tasks/<int:task_id>/summary/', TaskSummaryReportView.as_view(), name='task-summary-report'),
    path('unit/global/', GlobalUnitReportView.as_view(), name='global-unit-report'),
]