from .models import Enrollment, StudyGroup


def get_user_enrolled_unit_ids(user):
    return Enrollment.objects.filter(student=user).values_list("unit_id", flat=True)


def get_user_study_group_ids(user):
    return StudyGroup.objects.filter(members=user).values_list("id", flat=True)