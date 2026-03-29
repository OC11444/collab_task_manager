from django.conf import settings
from django.db import models
#create your models here for tables  school,depart,course,unit,
class School(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Department(models.Model):#creates a table
    name = models.CharField(max_length=150) #creates a column
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='departments')#introduces relations using DRY rule
    created_at = models.DateTimeField(auto_now_add=True)# creates timestamp when our record was created so we dont do it manual
   #display helper
    def __str__(self):
        return f"{self.name} ({self.school.name})"


class Course(models.Model):
    LEVEL_CHOICES = (
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('degree', 'Degree'),
        ('masters', 'Masters'),
    )
    name = models.CharField(max_length=200)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='degree')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


class Unit(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)

    # 1. Changed from ForeignKey to ManyToManyField to allow shared units
    courses = models.ManyToManyField(Course, related_name='units')

    # 2. Added strict choices for the current year of study
    YEAR_CHOICES = (
        (1, 'Year 1'),
        (2, 'Year 2'),
        (3, 'Year 3'),
        (4, 'Year 4'),
        (5, 'Year 5'),
    )
    year_of_study = models.IntegerField(choices=YEAR_CHOICES, default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name} (Year {self.year_of_study})"


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # This strict database rule prevents a student from enrolling in the exact same course twice!
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.name}"