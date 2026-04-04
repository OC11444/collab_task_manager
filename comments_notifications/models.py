from django.db import models
from django.conf import settings
from tasks.models import Task


class Comment(models.Model):
    """
    Represents a comment made by a user on a specific task.

    Fields:
        task: ForeignKey to the related Task.
        author: ForeignKey to the user who wrote the comment.
        content: The text content of the comment.
        created_at: Timestamp when the comment was created.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # newest comments first

    def __str__(self):
        return f"{self.author} → {self.task.title}"


class Notification(models.Model):
    """
    Represents a notification sent to a user.

    Fields:
        recipient: The user who receives the notification.
        task: (Optional) Related task.
        message: Notification message.
        notification_type: Type (comment, assignment, deadline, general).
        is_read: Read status.
        created_at: Timestamp.
    """
    NOTIFICATION_COMMENT = 'comment'
    NOTIFICATION_ASSIGNMENT = 'assignment'
    NOTIFICATION_DEADLINE = 'deadline'
    NOTIFICATION_GENERAL = 'general'

    NOTIFICATION_TYPES = [
        (NOTIFICATION_COMMENT, 'Comment'),
        (NOTIFICATION_ASSIGNMENT, 'Assignment'),
        (NOTIFICATION_DEADLINE, 'Deadline'),
        (NOTIFICATION_GENERAL, 'General'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_notifications'
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='task_notifications'
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default=NOTIFICATION_GENERAL
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        task_info = f" | Task: {self.task.title}" if self.task else ""
        return f"{self.recipient} | {self.notification_type}{task_info} | Message: {self.message[:30]}{'...' if len(self.message) > 30 else ''} | Read: {self.is_read}"
    class Meta:
        ordering = ['-created_at']  # newest first