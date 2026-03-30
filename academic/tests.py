# academic/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase
from .models import School, Department, Course, Unit

class AcademicAPITests(APITestCase):
    def setUp(self):
        # Create the hierarchy
        self.school = School.objects.create(name="Engineering")
        self.dept = Department.objects.create(name="Software", school=self.school)
        self.course = Course.objects.create(name="Computer Science", department=self.dept)
        
        # FIX: Use 'code' to match your updated model
        self.unit = Unit.objects.create(
            name="Programming", 
            code="CS101", 
            course=self.course
        )

    def test_get_schools(self):
        response = self.client.get('/api/academic/schools/')
        self.assertEqual(response.status_code, 200)

    def test_create_unit(self):
        # FIX: Use 'code' in the payload too
        data = {"name": "Data Structures", "code": "CS102", "course": self.course.id}
        response = self.client.post('/api/academic/units/', data)
        self.assertEqual(response.status_code, 201)