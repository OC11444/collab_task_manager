from rest_framework.routers import DefaultRouter

from .views import TaskSubmissionViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'task-submissions', TaskSubmissionViewSet, basename='task-submission')

urlpatterns = router.urls