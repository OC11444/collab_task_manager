# reports/views.py
from django.db.models import Max
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import UnitPerformanceSnapshot
from .serializers import UnitDashboardSerializer

class LecturerDashboardView(generics.ListAPIView):
    serializer_class = UnitDashboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        lecturer_id = self.request.user.id

        # 1. Get the latest snapshot ID for each unit taught by this lecturer
        # This approach avoids the 'LIMIT in IN subquery' error
        latest_snapshot_ids = (
            UnitPerformanceSnapshot.objects
            .filter(lecturer_id=lecturer_id)
            .values('unit_id')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )

        # 2. Return those specific snapshots
        return UnitPerformanceSnapshot.objects.filter(
            id__in=list(latest_snapshot_ids) # Cast to list to force execution
        ).order_by('-timestamp')