from django.db import models
from django.conf import settings

class School(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='departments')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.school.name})"

class Course(models.Model):
    name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=255)
    # Changed unit_code to code to match Dev 2's tests
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units', null=True, blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='enrolled_students')
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} in {self.unit.unit_code}"