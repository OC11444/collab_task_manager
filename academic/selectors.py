"""
Module: academic
Author: Griffins Majaliwa

Extracts the database queries for student permissions into separate functions. This way, if other apps in the monolith need to check what a student is enrolled in, they don't have to write duplicate query logic.
"""
from .models import Enrollment, StudyGroup


def get_user_enrolled_unit_ids(user):
    """
        Grabs a flat list of unit IDs a student belongs to. We use this heavily in the tasks module to hide assignments for classes the student isn't taking.
        """
    return Enrollment.objects.filter(student=user).values_list("unit_id", flat=True)


def get_user_study_group_ids(user):
    return StudyGroup.objects.filter(members=user).values_list("id", flat=True)