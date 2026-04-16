from django.db.models import Max
from .models import UnitPerformanceSnapshot

def get_latest_unit_snapshots_for_lecturer(user):
    """
    Business Logic: Retrieve the most recent snapshot for every unit
    associated with the given lecturer.
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