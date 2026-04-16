# comments_notifications/urls.py
from django.urls import path
from .views import TaskCommentAPIView, TaskSubmissionCommentAPIView

urlpatterns = [
    # Matches reverse("task-comments", kwargs={"pk": self.task.id})
    path('task/<int:pk>/', TaskCommentAPIView.as_view(), name='task-comments'),

    # Matches reverse("tasksubmission-comments", kwargs={"pk": self.submission.id})
    path('submission/<int:pk>/', TaskSubmissionCommentAPIView.as_view(), name='tasksubmission-comments'),
]