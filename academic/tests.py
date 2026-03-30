from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import School, Department, Course, Unit

class AcademicAPITests(APITestCase):
    def setUp(self):
        # 1. Create School
        self.school = School.objects.create(name="School of Computing")
        
        # 2. Create Department
        self.dept = Department.objects.create(name="IT", school=self.school)
        
        # 3. Create Course (Required by your Unit model)
        self.course = Course.objects.create(
            name="BSc Information Technology", 
            course_code="BIT", 
            department=self.dept
        )
        
        # 4. Create Unit (Linking to Course)
        self.unit = Unit.objects.create(
            name="Database Systems", 
            unit_code="BIT210", 
            course=self.course
        )

    def test_get_schools(self):
        """Test if we can list schools via API"""
        url = reverse('school-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_unit(self):
        """Test if we can create a new unit via API"""
        url = reverse('unit-list')
        data = {
            "name": "Data Structures",
            "unit_code": "CS102",
            "course": self.course.id # Use course ID here
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Unit.objects.count(), 2)