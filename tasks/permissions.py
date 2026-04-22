"""
Module: tasks
Author: Mecrimson

Acts as the security gatekeeper for the module. We explicitly check roles and enrollments here so that students cannot bypass the system to edit assignments or view other people's grades.
"""
from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
        Prevents students from altering global assignment details. They are allowed to read the instructions, but only staff members can change due dates or descriptions.
        """


    def has_permission(self, request, view):
        # Authenticated users can always use 'SAFE' methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Only staff can perform 'Write' actions (POST, PUT, DELETE)
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsOwnerOrStaff(permissions.BasePermission):
    """
        Enforces privacy for student grades and submissions. A student can only load their own specific submission record, while lecturers are allowed to load anyone's record to grade it.
        """

    def has_object_permission(self, request, view, obj):
        # Staff can see everything
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Students can only see/edit their own submission record
        return obj.student == request.user


class IsStaffOrStudentEnrolled(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Staff can do anything; Students can do GET or PATCH
        if not (request.user.is_staff or request.user.is_superuser):
            return request.method in permissions.SAFE_METHODS or request.method == 'PATCH'

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        from django.apps import apps
        # Use the app registry to maintain loose coupling
        Enrollment = apps.get_model('academic', 'Enrollment')
        unit_ids = Enrollment.objects.filter(student=request.user).values_list('unit_id', flat=True)

        # Students must be enrolled in the unit to view or update their status
        if obj.unit_id in unit_ids:
            return request.method in permissions.SAFE_METHODS or request.method == 'PATCH'

        return False