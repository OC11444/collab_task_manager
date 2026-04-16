#comments_notifications/services.py    
from django.contrib.contenttypes.models import ContentType

from .models import Comment, Notification
from .signals import comment_created


def create_comment(author, content, target_object, parent=None):
    """
    Standardizes comment creation across any model in the system.
    """
    content_type = ContentType.objects.get_for_model(
        target_object,
        for_concrete_model=False,
    )

    new_comment = Comment.objects.create(
        author=author,
        content=content,
        parent=parent,
        content_type=content_type,
        object_id=target_object.pk,
    )

    comment_created.send(
        sender=Comment,
        comment=new_comment,
        target_object=target_object,
    )

    return new_comment


def create_notification(recipient, message, target_object=None):
    """
    Creates a notification. If target_object is provided, it enables
    contextual routing for the frontend.
    """
    target_ct = None
    target_id = None

    if target_object:
        target_ct = ContentType.objects.get_for_model(target_object)
        target_id = target_object.pk

    return Notification.objects.create(
        recipient=recipient,
        message=message,
        target_content_type=target_ct,
        target_object_id=target_id
    )