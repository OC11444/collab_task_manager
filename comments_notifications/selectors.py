# comments_notifications/selectors.py
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Comment

User = get_user_model()

def get_comments_for_object(target_object, user):
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

    # 3. RBAC: "WhatsApp Style" for Tasks
    # If the target is a Task (Unit discussion), allow everyone to see all comments
    if target_object.__class__.__name__ == 'Task':
        return qs.order_by('created_at')

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
