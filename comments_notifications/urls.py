# comments_notifications/urls.py
from django.urls import path
from .views import TaskCommentAPIView

urlpatterns = [
    # This allows: POST /api/comments/task/1/
    path('task/<int:task_id>/', TaskCommentAPIView.as_view(), name='task-comments-standalone'),
]