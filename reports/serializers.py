from rest_framework import serializers
from .models import UnitPerformanceSnapshot

class UnitDashboardSerializer(serializers.ModelSerializer):
    """
    Serializes the latest snapshot and calculates trend indicators
    for the Staff Dashboard.
    """
    trend_submission_rate = serializers.SerializerMethodField()

    class Meta:
        model = UnitPerformanceSnapshot
        fields = [
            'unit_id',
            'submission_rate',
            'on_time_ratio',
            'pending_reviews',
            'overdue_feedback',
            'snapshot_type',
            'timestamp',
            'trend_submission_rate'
        ]

    def get_trend_submission_rate(self, obj):
        """
        Logic to compare current snapshot with the previous one
        to calculate the trend percentage.
        """
        previous_snapshot = UnitPerformanceSnapshot.objects.filter(
            unit_id=obj.unit_id,
            timestamp__lt=obj.timestamp
        ).first()

        if not previous_snapshot:
            return 0.0

        return round(float(obj.submission_rate - previous_snapshot.submission_rate), 2)