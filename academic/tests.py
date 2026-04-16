from django.test import TestCase
from rest_framework.test import APITestCase
from users.models import User
from .models import School, Department, Course, Unit


class AcademicAPITests(APITestCase):
    def setUp(self):
        # Create the hierarchy
        self.school = School.objects.create(name="Engineering")
        self.dept = Department.objects.create(name="Software", school=self.school)
        self.course = Course.objects.create(name="Computer Science", department=self.dept)

        self.unit = Unit.objects.create(
            name="Programming",
            code="CS101",
            course=self.course
        )

        self.url = "/api/academic/units/"

    def test_get_schools(self):
        user = User.objects.create_user(
            username="test_user",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/academic/schools/')
        self.assertEqual(response.status_code, 200)

    def test_create_unit(self):
        user = User.objects.create_user(
            username="staff_user",
            password="<PASSWORD>",
            is_staff=True,
            role="staff"
        )
        self.client.force_authenticate(user=user)

        data = {"name": "Data Structures", "code": "CS102", "course": self.course.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)