from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from users.models import User
from academic.models import School, Department, Course, Unit
from .models import Task, TaskSubmission
#create ur tests here
class TaskSubmissionTestCase(TestCase):
    def setUp(self):
        # 1. Build the required academic chain
        self.school = School.objects.create(name="Tech School")
        self.dept = Department.objects.create(name="CS Dept", school=self.school)
        self.course = Course.objects.create(name="BSc CS", department=self.dept)
        self.unit = Unit.objects.create(name="Programming", code="CS101")
        self.unit.courses.add(self.course)

        # 2. Create the test users
        self.lecturer = User.objects.create(username="lecturer1", role="staff")
        self.student = User.objects.create(username="student1", role="student")

        # 3. Create a task with a deadline set to YESTERDAY
        yesterday = timezone.now() - timedelta(days=1)
        self.task = Task.objects.create(
            title="Test Assignment",
            unit=self.unit,
            created_by=self.lecturer,
            due_date=yesterday
        )

    def test_is_late_property(self):
        # 4. Create a submission right NOW
        submission = TaskSubmission.objects.create(
            task=self.task,
            student=self.student,
            submission_link="https://drive.google.com/test"
        )

        # 5. The actual test: Ask Python to mathematically prove it is late
        # assertTrue means the test PASSES if submission.is_late is True
        self.assertTrue(submission.is_late)