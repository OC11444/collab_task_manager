"""
Module: reports
Author: Tipeii

Extracts complex database queries out of the views. This keeps our views clean and makes it easier to reuse these specific data fetches elsewhere.
"""
from django.db.models import Max
from .models import UnitPerformanceSnapshot

def get_latest_unit_snapshots_for_lecturer(user):
    """
        Since we store multiple historical snapshots for every unit, this function filters through the noise to grab only the single most recent record for each unit taught by this specific lecturer.
        """

    # 1. Get the latest snapshot ID for each unit taught by this lecturer
    latest_snapshot_ids = (
        UnitPerformanceSnapshot.objects
        .filter(lecturer_id=user.id)
        .values('unit_id')
        .annotate(latest_id=Max('id'))
        .values_list('latest_id', flat=True)
    )

    # 2. Return those specific snapshots
    return UnitPerformanceSnapshot.objects.filter(
        id__in=list(latest_snapshot_ids)
    ).order_by('-timestamp')