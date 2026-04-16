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

    # 2. RBAC: Teachers and Lecturers see all comments
    user_role = getattr(user, 'role', '').lower()
    if user_role in ['teacher', 'lecturer', 'admin']:
        return qs.order_by('created_at')

    # 3. RBAC: Student Visibility Logic
    # Students see their own comments OR comments from a teacher
    criteria = Q(author=user) | Q(author__role__in=['teacher', 'lecturer'])

    # Modular Check: If the object has study groups, allow members to see each other's work
    if hasattr(target_object, 'study_groups'):
        # Find groups the current user belongs to that are assigned to this task
        shared_groups = target_object.study_groups.filter(members=user)
        if shared_groups.exists():
            # Add visibility for anyone in those shared groups
            criteria |= Q(author__in=User.objects.filter(study_groups__in=shared_groups))

    return qs.filter(criteria).distinct().order_by('created_at')