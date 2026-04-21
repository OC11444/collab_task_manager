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