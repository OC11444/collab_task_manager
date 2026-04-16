#comments_notifications/selectors.py
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from .models import Comment


def get_comments_for_object(target_object, user):
    """
    Fetches top-level comments for an object enforcing strict RBAC.
    """
    content_type = ContentType.objects.get_for_model(
        target_object,
        for_concrete_model=False,
    )

    # 1. Base query: Get top-level comments for this specific object
    qs = Comment.objects.filter(
        content_type=content_type,
        object_id=target_object.pk,
        parent__isnull=True  # Only fetch top-level (serializer handles replies)
    ).select_related('author')

    # 2. RBAC Privacy Filter
    if getattr(user, 'role', '') == 'student':
        # Students ONLY see their own comments OR comments written by a lecturer
        qs = qs.filter(Q(author=user) | Q(author__role='lecturer'))

    # If user is a lecturer, they bypass the filter and see everything
    return qs.order_by('-created_at')