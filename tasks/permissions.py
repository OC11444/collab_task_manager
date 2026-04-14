from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Allows staff members to create/edit tasks,
    but students can only view them.
    """

    def has_permission(self, request, view):
        # Authenticated users can always use 'SAFE' methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Only staff can perform 'Write' actions (POST, PUT, DELETE)
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Used for submissions: Only the student who owns the submission
    or a staff member can view/edit the specific object.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can see everything
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Students can only see/edit their own submission record
        return obj.student == request.user