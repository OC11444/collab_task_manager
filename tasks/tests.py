from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from academic.models import Unit, Enrollment
from comments_notifications.models import Notification
from tasks.models import Task, TaskSubmission

User = get_user_model()


class TestCommentIntegration(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lecturer = User.objects.create_user(
            username="lecturer_user",
            password="<PASSWORD_PLACEHOLDER>",
            is_staff=True,
        )
        cls.student = User.objects.create_user(
            username="student_user",
            password="<PASSWORD_PLACEHOLDER>",
        )
        cls.student2 = User.objects.create_user(
            username="student_user_2",
            password="<PASSWORD_PLACEHOLDER>",
        )

        cls.unit = Unit.objects.create(
            name="Software Engineering",
            code="SE101",
            lecturer=cls.lecturer,
        )

        Enrollment.objects.create(student=cls.student, unit=cls.unit)
        Enrollment.objects.create(student=cls.student2, unit=cls.unit)

        cls.task = Task.objects.create(
            title="Assignment 1",
            unit=cls.unit,
            created_by=cls.lecturer,
            due_date=timezone.now() + timedelta(days=7),
        )

        cls.submission = TaskSubmission.objects.create(
            task=cls.task,
            student=cls.student,
        )

    def test_submission_feedback_creates_notification(self):
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("tasksubmission-comments", kwargs={"pk": self.submission.id})
        response = self.client.post(
            url,
            {"content": "Please review your citations."},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first().recipient, self.student)

    def test_public_task_comment_creates_fan_out_notifications(self):
        Notification.objects.all().delete()
        self.client.force_authenticate(user=self.student)

        url = reverse("task-comments", kwargs={"pk": self.task.id})
        response = self.client.post(
            url,
            {"content": "Can someone clarify the requirements for question 2?"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 2)

        recipients = list(Notification.objects.values_list("recipient", flat=True))
        self.assertIn(self.lecturer.id, recipients)
        self.assertIn(self.student2.id, recipients)
        self.assertNotIn(self.student.id, recipients)