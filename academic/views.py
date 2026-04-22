"""
Module: academic
Author: Griffins Majaliwa

Controls how users interact with the academic structure. We enforce a strict read-only policy for students here, while allowing staff members to build out the courses and manage enrollments.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS, AllowAny
from rest_framework.request import Request

from .models import School, Department, Course, Unit, Enrollment
from .serializers import (
    SchoolSerializer, DepartmentSerializer, CourseSerializer,
    UnitSerializer, EnrollmentSerializer
)


# Custom Permission: Anyone can read, only Staff can write
class IsStaffOrReadOnly(BasePermission):
    """
        A custom security check. Students can look at the list of courses or units, but only lecturers and admins are allowed to make changes to the curriculum.
        """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsStaffOrReadOnly]


class DepartmentViewSet(viewsets.ModelViewSet):
    """
        We override the default query here to allow the frontend to filter departments by school using URL parameters. The CourseViewSet and UnitViewSet do the same thing for their parent models.
        """
    queryset = Department.objects.all() # Router needs this for basename
    serializer_class = DepartmentSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        request: Request = self.request
        queryset = self.queryset
        school_id = request.query_params.get('school')
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        return queryset


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all() # Router needs this for basename
    serializer_class = CourseSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        request: Request = self.request
        queryset = self.queryset
        dept_id = request.query_params.get('department')
        if dept_id:
            queryset = queryset.filter(department_id=dept_id)
        return queryset


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all() # Router needs this for basename
    serializer_class = UnitSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        request: Request = self.request
        queryset = self.queryset
        course_id = request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
        Manages who is taking what class. We restrict the view so a student only sees their own class schedule, but staff members can see the entire university's enrollment list. We also force the student ID to match the logged-in user if a student tries to enroll themselves, preventing them from enrolling other people.
        """
    queryset = Enrollment.objects.all() # Router needs this for basename
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        return self.queryset.filter(student=user)

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(student=self.request.user)
        else:
            serializer.save()