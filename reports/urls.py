from django.urls import path
from .views import LecturerDashboardView

urlpatterns = [
    path('dashboard/lecturer/', LecturerDashboardView.as_view(), name='lecturer-dashboard'),
]