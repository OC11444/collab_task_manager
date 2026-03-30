# tasks/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from academic.models import Unit

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    allow_late_submissions = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.unit})"

class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    submission_link = models.URLField(max_length=500)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_late(self):
        """
        Check if the submission was made after the task's due date.
        If no due date exists, it's not late.
        """
        if not self.task.due_date:
            return False
        
        # Logic: Compare the submission timestamp to the task deadline
        return self.submitted_at > self.task.due_date

    class Meta:
        unique_together = ('task', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.task.title}"