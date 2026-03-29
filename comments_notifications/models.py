#comments_notifications/models.py
from django.db import models
from django.conf import settings
from tasks.models import Task
#create ur models here
class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


class Notification(models.Model):
    # The user RECEIVING the notification
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')

    # The actual alert text
    message = models.CharField(max_length=255)

    # Tracks if they have clicked the notification yet
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username} - Read: {self.is_read}"