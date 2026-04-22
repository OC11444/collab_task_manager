"""
Module: tasks
Author: Mecrimson

We originally used Django signals to handle notifications, but it led to bugs where alerts would fire twice. We keep this file to explicitly intercept and pass on the comment_created signal, ensuring all notification logic stays visible inside the views.
"""
from django.dispatch import receiver

from comments_notifications.signals import comment_created
from comments_notifications.services import create_notification
from tasks.models import Task, TaskSubmission


@receiver(comment_created)
def handle_comment_created(sender, comment, target_object, **kwargs):
    """
    Signal receiver for comment creation.

    NOTE: Notification logic has been moved to the Views (Explicit Logging)
    to follow the 'simple and reliable' architecture and avoid double notifications.
    """
    pass