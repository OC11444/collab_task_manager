"""
Module: reports
Author: Tipeii

Converts the raw database snapshot records into clean JSON objects for the frontend dashboard to display.
"""
from rest_framework import serializers
from .models import UnitPerformanceSnapshot

class UnitDashboardSerializer(serializers.ModelSerializer):
    """
        Formats the performance metrics for the staff view. We also calculate a trend indicator here so the lecturer knows if things are improving or getting worse.
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
            Looks up the previous historical snapshot for this unit and compares it to the current one. This gives the frontend a simple percentage difference to show as an up or down arrow.
            """

        previous_snapshot = UnitPerformanceSnapshot.objects.filter(
            unit_id=obj.unit_id,
            timestamp__lt=obj.timestamp
        ).first()

        if not previous_snapshot:
            return 0.0

        return round(float(obj.submission_rate - previous_snapshot.submission_rate), 2)