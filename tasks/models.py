#tasks/models.py
from django.db import models
from django.conf import settings
from academic.models import Unit

#create ur models here
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()

    # Allows late submission .approved by checkbox in frontend
    allow_late_submissions = models.BooleanField(default=False)

    # Linking to the User table (the Staff member who created it)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')

    # Linking to the Academic table (the Unit this task belongs to)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='tasks')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates whenever the task is edited

    def __str__(self):
        return f"{self.title} ({self.unit.code})"


class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')

    # Using URLField to store cloudlinks instead of uploading raw data to our server.this will increase performance limit costs and help scale our system
    submission_link = models.URLField(max_length=500)

    # Tracks the exact moment they first clicked submit,when did stud a submit their work
    submitted_at = models.DateTimeField(auto_now_add=True)

    # If they realize they made a mistake and swap the link, this updates automatically
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_late(self):
        # This is your exact logic, permanently attached to the model!
        return self.submitted_at > self.task.due_date

    class Meta:
        # Strict rule: A student can only have ONE submission record for a specific task.
        unique_together = ('task', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.task.title}"