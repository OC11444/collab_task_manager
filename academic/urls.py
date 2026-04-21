#academic/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolViewSet, DepartmentViewSet, CourseViewSet,
    UnitViewSet, EnrollmentViewSet
)

# This creates the API endpoints automatically
router = DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'units', UnitViewSet)

# FIX: Added basename='enrollment' to satisfy the router after securing the ViewSet
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]