from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS

from .models import School, Department, Course, Unit, Enrollment
from .serializers import (
    SchoolSerializer, DepartmentSerializer, CourseSerializer,
    UnitSerializer, EnrollmentSerializer
)


# Custom Permission: Anyone can read, only Staff can write
class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsStaffOrReadOnly]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsStaffOrReadOnly]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsStaffOrReadOnly]


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsStaffOrReadOnly]


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    # Security: Ensure students only see their own enrollments
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=user)

    # Security: Ensure when a student enrolls, it locks to their user ID
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(student=self.request.user)
        else:
            serializer.save()