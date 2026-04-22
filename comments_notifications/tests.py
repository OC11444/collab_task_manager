from typing import Any, Type
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Model

# Local imports
from .models import Notification
from .services import create_comment

User = get_user_model()

# Use type hints to satisfy the editor's static analysis
Task: Any = apps.get_model('tasks', 'Task')
Unit: Any = apps.get_model('academic', 'Unit')
Course: Any = apps.get_model('academic', 'Course')
Department: Any = apps.get_model('academic', 'Department')
School: Any = apps.get_model('academic', 'School')
StudyGroup: Any = apps.get_model('academic', 'StudyGroup')
Enrollment: Any = apps.get_model('academic', 'Enrollment')  # Added Enrollment model


class CommentPrivacyAndNotificationTests(APITestCase):
    client: APIClient  # Tells editor self.client has force_authenticate

    def setUp(self):
        # 1. Create Academic Hierarchy
        self.school = School.objects.create(name="Engineering")
        self.dept = Department.objects.create(name="Software", school=self.school)
        self.course = Course.objects.create(name="CS", department=self.dept)

        # 2. Create Users with ROLES
        self.teacher = User.objects.create_user(username="t1", password="p", role="teacher", is_staff=True)
        self.student_a = User.objects.create_user(username="s_a", password="p", role="student")
        self.student_b = User.objects.create_user(username="s_b", password="p", role="student")
        self.student_c = User.objects.create_user(username="s_c", password="p", role="student")

        # 3. Create Unit and Study Group
        self.unit = Unit.objects.create(name="Prog", code="CS1", course=self.course, lecturer=self.teacher)

        # Explicitly Enroll students in the unit so they can see unit-wide tasks
        Enrollment.objects.create(student=self.student_a, unit=self.unit)
        Enrollment.objects.create(student=self.student_b, unit=self.unit)
        Enrollment.objects.create(student=self.student_c, unit=self.unit)

        self.group = StudyGroup.objects.create(name="Group A", unit=self.unit)
        self.group.members.add(self.student_a, self.student_b, self.student_c)

        # 4. Setup Tasks with REQUIRED due_date
        self.task = Task.objects.create(
            title="Task",
            created_by=self.teacher,
            unit=self.unit,

            due_date=timezone.now() + timedelta(days=7)
        )
        self.group_task = Task.objects.create(
            title="Group Task", created_by=self.teacher, unit=self.unit,
            due_date=timezone.now() + timedelta(days=14)
        )
        self.group_task.study_groups.add(self.group)

    def test_student_cannot_see_other_students_comments(self):
        create_comment(author=self.student_a, content="X", target_object=self.task)
        self.client.force_authenticate(user=self.student_b)
        response = self.client.get(f'/api/tasks/{self.task.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Uses status import
        self.assertEqual(len(response.data), 0)

    def test_teacher_can_see_all_comments(self):
        create_comment(author=self.student_a, content="X", target_object=self.task)
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/tasks/{self.task.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_group_task_visibility(self):
        create_comment(author=self.student_a, content="X", target_object=self.group_task)
        self.client.force_authenticate(user=self.student_c)
        response = self.client.get(f'/api/tasks/{self.group_task.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_notification_not_sent_to_sender(self):
        create_comment(author=self.student_a, content="X", target_object=self.task)
        Notification.objects.filter(recipient=self.teacher).delete()
        create_comment(author=self.teacher, content="Y", target_object=self.task)
        self.assertEqual(Notification.objects.filter(recipient=self.teacher).count(), 0)