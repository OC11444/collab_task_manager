from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from academic.models import School, Department, Course, Unit, Enrollment
from tasks.models import Task, TaskSubmission
from reports.models import UnitPerformanceSnapshot
from reports.services import ReportService

User = get_user_model()


class UnifiedSystemTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 1. The Setup: 1 Lecturer, 2 Students
        cls.lec = User.objects.create_user(username="lec_user", is_staff=True, password="pin")
        cls.stu1 = User.objects.create_user(username="student_1", password="pin")
        cls.stu2 = User.objects.create_user(username="student_2", password="pin")

        # 2. The Academic Staircase (Fixed for IntegrityErrors)
        school = School.objects.create(name="Science")
        dept = Department.objects.create(name="IT", school=school)
        cls.unit = Unit.objects.create(name="Coding", code="CS1", lecturer=cls.lec)

        Enrollment.objects.create(student=cls.stu1, unit=cls.unit)
        Enrollment.objects.create(student=cls.stu2, unit=cls.unit)

        # 3. The Job: 1 Task for the whole class
        cls.task = Task.objects.create(
            title="Final Project",
            unit=cls.unit,
            created_by=cls.lec,
            due_date="2026-12-31T00:00:00Z"
        )

    def test_report_lifecycle(self):
        """Verify that reports correctly reflect submissions after a snapshot."""
        url = reverse('lecturer-dashboard')

        # --- PHASE 1: Initial State (0% Completion) ---
        ReportService.create_unit_snapshot(self.unit.id, self.lec.id)

        self.client.force_authenticate(user=self.lec)
        response = self.client.get(url)
        self.assertEqual(float(response.data[0]['submission_rate']), 0.0)

        # --- PHASE 2: Half the class submits ---
        # No live trigger here - system stays fast!
        TaskSubmission.objects.create(task=self.task, student=self.stu1)

        # --- PHASE 3: The "Whole Job" Calculation ---
        # This simulates your 'past due date' or 'end of day' batch run
        ReportService.create_unit_snapshot(self.unit.id, self.lec.id)

        response = self.client.get(url)

        # 1 submission / (2 students * 1 task) = 50%
        # Trend should be 50 (Current 50 - Previous 0)
        self.assertEqual(float(response.data[0]['submission_rate']), 50.0)
        self.assertEqual(float(response.data[0]['trend_submission_rate']), 50.0)

        print("\n✅ Unified Test: Academic -> Task -> Submission -> Report: SUCCESS")