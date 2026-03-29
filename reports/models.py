from django.db import models
from django.conf import settings

#create ur models here
class ReportSnapshot(models.Model):
    REPORT_TYPES = (
        ('task_completion', 'Task Completion Rates'),
        ('student_performance', 'Student Performance'),
        ('system_usage', 'System Usage Stats'),
    )

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)

    # This is where the magic happens for your future AI dataset
    data = models.JSONField()

    # Using SET_NULL so if a staff member leaves, we don't lose the historical reports they generated
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}"