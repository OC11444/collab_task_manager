from django.contrib.contenttypes.models import ContentType

from .models import Comment


def get_comments_for_object(target_object):
    content_type = ContentType.objects.get_for_model(
        target_object,
        for_concrete_model=False,
    )

    return Comment.objects.filter(
        content_type=content_type,
        object_id=target_object.pk,
    ).select_related('author')