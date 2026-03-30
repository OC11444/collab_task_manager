# tasks/tests.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from academic.models import Unit, Course, Department, School
from .models import Task, TaskSubmission

User = get_user_model()

class TaskSubmissionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', password='password')
        self.staff = User.objects.create_user(username='staff1', password='password', is_staff=True)
        
        # Setup basic academic structure for the task
        self.school = School.objects.create(name="Test School")
        self.dept = Department.objects.create(name="Test Dept", school=self.school)
        self.course = Course.objects.create(name="Test Course", department=self.dept)
        
        # FIX: Create unit and link to course directly
        self.unit = Unit.objects.create(name="Calculus", code="MATH101", course=self.course)
        
        # Create a task that was due yesterday
        self.task = Task.objects.create(
            title="Assignment 1",
            due_date=timezone.now() - timedelta(days=1),
            unit=self.unit,
            created_by=self.staff
        )

    def test_is_late_property(self):
        # Create a submission now (1 day late)
        submission = TaskSubmission.objects.create(
            task=self.task,
            student=self.user,
            submission_link="https://drive.google.com/test"
        )
        # This checks the logic we added to tasks/models.py
        self.assertTrue(submission.is_late)