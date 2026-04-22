"""
Module: comments_notifications
Author: OC11444

Handles the data retrieval for comments. We put the privacy wall logic here to keep our views clean and ensure data security is applied at the query level.
"""
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Comment

User = get_user_model()

def get_comments_for_object(target_object, user):
    """
        Applies role-based access control to the comment threads. Staff members can see the whole conversation, but students are restricted to seeing only their own comments or threads shared within their specific study group.
        """
    content_type = ContentType.objects.get_for_model(target_object, for_concrete_model=False)

    # 1. Base query: Top-level comments only
    qs = Comment.objects.filter(
        content_type=content_type,
        object_id=target_object.pk,
        parent__isnull=True
    ).select_related('author')

    # 2. RBAC: Staff and Admins see all comments
    user_role = getattr(user, 'role', '').lower()
    if user_role in ['staff', 'teacher', 'lecturer', 'admin'] or getattr(user, 'is_staff', False):
        return qs.order_by('created_at')
        # 3. RBAC: Privacy Wall Logic
        # Everyone sees their own comments and anything from a Teacher/Lecturer
        criteria = Q(author=user) | Q(author__role__in=['staff', 'teacher', 'lecturer'])

        # ACCESS RULE A: Individual Privacy
        # If I am the specific student assigned to this task, I see the whole conversation
        if hasattr(target_object, 'assigned_to') and target_object.assigned_to == user:
            return qs.order_by('created_at')

        # ACCESS RULE B: Group Collaboration (WhatsApp Style)
        # If this object involves study groups, members of my group can see the discussion
        if hasattr(target_object, 'study_groups'):
            shared_groups = target_object.study_groups.filter(members=user)
            if shared_groups.exists():
                # Allow visibility for anyone in my shared group
                criteria |= Q(author__in=User.objects.filter(study_groups__in=shared_groups))

        return qs.filter(criteria).distinct().order_by('created_at')



    # For Submissions (Private Feedback), keep strict visibility
    criteria = Q(author=user) | Q(author__role__in=['staff', 'teacher', 'lecturer'])

    # Modular Check: If the object has study groups, allow members to see each other's work
    if hasattr(target_object, 'study_groups'):
        # Find groups the current user belongs to that are assigned to this task
        shared_groups = target_object.study_groups.filter(members=user)
        if shared_groups.exists():
            # Add visibility for anyone in those shared groups
            criteria |= Q(author__in=User.objects.filter(study_groups__in=shared_groups))

    return qs.filter(criteria).distinct().order_by('created_at')
