from django.contrib.contenttypes.models import ContentType

from .models import Comment, Notification
from .signals import comment_created


def create_comment(author, content, target_object, parent=None):
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


def create_notification(recipient, message):
    return Notification.objects.create(
        recipient=recipient,
        message=message,
    )