"""
Module: academic
Author: Griffins Majaliwa

Sets up the structural hierarchy of the school. We map out schools, departments, courses, and units here to act as the backbone for student enrollments and study groups.
"""
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
    # FIX 1: Temporarily allow null to unblock the migration engine
    course_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.name


class Unit(models.Model):
    """
        Represents a single subject taught in a semester. We tie this directly to a specific lecturer so the system knows who is in charge of grading the assignments.
        """
    name = models.CharField(max_length=255)
    # Changed unit_code to code to match Dev 2's tests
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units', null=True, blank=True)
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lectured_units',
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(models.Model):
        """
        Acts as the bridge between a student and a unit. The rest of the system heavily relies on this table to check if a student actually has permission to see assignments or submit work for a class.
        """

        student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
        # FIX 3: Temporarily allow null to unblock the migration engine for the unit field
        unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='enrolled_students', null=True ,blank=True)
        date_enrolled = models.DateField(auto_now_add=True)

        def __str__(self):
            # FIX 2: Corrected the attribute reference to prevent a crash
            return f"{self.student.username} in {self.unit.code}"


class StudyGroup(models.Model):
    """
        Allows students to form smaller teams within a massive unit to collaborate on group projects or share private comment threads.
        """
    name = models.CharField(max_length=255)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='study_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='study_groups')

    def __str__(self):
        return self.name