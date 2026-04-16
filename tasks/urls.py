from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskSubmissionViewSet

router = DefaultRouter()

# Register submissions first so they are not matched by the empty task prefix
router.register(r'submissions', TaskSubmissionViewSet, basename='task-submission')

# Register tasks last at the root
router.register(r'', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]