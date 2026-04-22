"""
Module: comments_notifications
Author: OC11444

Centralizes the logic for creating comments and alerts. This prevents us from having to rewrite the exact same save logic inside every single view that needs to accept a comment.
"""
from django.contrib.contenttypes.models import ContentType

from .models import Comment, Notification
from .signals import comment_created


def create_comment(author, content, target_object, parent=None):
    """
        Builds the generic relationship for a new comment and fires off a custom signal to let the rest of the application know a new message was posted.
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


def create_notification(recipient, title, message, target_object=None):
    """
        Logs the actual alert into the database. We format the data as 'Actor did Action' to make it easy for the frontend to display a readable sentence.
        """
    target_ct = None
    target_id = None

    if target_object:
        target_ct = ContentType.objects.get_for_model(target_object)
        target_id = target_object.pk

    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        target_content_type=target_ct,
        target_object_id=target_id
    )