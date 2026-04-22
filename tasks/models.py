#tasks/models.py
"""
Module: tasks
Author: Mecrimson

Defines the database schema for assignments and student submissions. We separate the main Task from the TaskSubmission so that one assignment can be tracked individually by hundreds of students without duplicating the main instructions.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    """
        The main assignment template created by a lecturer. It holds the global rules like due dates and priority for everyone enrolled in the unit.
        """
    PRIORITY_HIGH = 'High'
    PRIORITY_MEDIUM = 'Medium'
    PRIORITY_LOW = 'Low'

    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_LOW, 'Low'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    allow_late_submissions = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    unit = models.ForeignKey('academic.Unit', on_delete=models.CASCADE, related_name='tasks')
    study_groups = models.ManyToManyField('academic.StudyGroup', related_name='tasks', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.unit})"


class TaskSubmission(models.Model):
    """
        Acts as a pivot table connecting a specific student to a specific task. This is where we store their personal Kanban status, their uploaded work link, and the grade the lecturer gives them.
        """
    STATUS_TO_DO = 'to_do'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'

    STATUS_CHOICES = [
        (STATUS_TO_DO, 'To Do'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_DONE, 'Done'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    submission_link = models.URLField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TO_DO)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_late(self):
        if not self.task.due_date:
            return False
        return self.submitted_at > self.task.due_date

    class Meta:
        unique_together = ('task', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.task.title} ({self.status})"