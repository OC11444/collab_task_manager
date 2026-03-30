# tasks/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from academic.models import Unit

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()

    # Allows late submission .approved by checkbox in frontend
    allow_late_submissions = models.BooleanField(default=False)

    # Linking to the User table (the Staff member who created it)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_tasks'
    )

    # Linking to the Academic table (the Unit this task belongs to)
    unit = models.ForeignKey(
        Unit, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.unit.unit_code if hasattr(self.unit, 'unit_code') else self.unit.name})"


class TaskSubmission(models.Model):
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='submissions'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='submissions'
    )

    # URLField for cloud links to optimize performance and scale
    submission_link = models.URLField(max_length=500)

    # Tracks the exact moment of submission
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Updates automatically if the student swaps the link
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_late(self):
        """
        Logic fix: Checks if the submission was made after the deadline.
        Includes a safety check for tasks without a defined due_date.
        """
        if not self.task or not self.task.due_date:
            return False
        return self.submitted_at > self.task.due_date

    class Meta:
        # Ensures a student has only one submission record per task
        unique_together = ('task', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.task.title}"