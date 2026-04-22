#collab_task_manager/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 1. Configure the API Documentation (Swagger)
schema_view = get_schema_view(
    openapi.Info(
        title="Collab Task Manager API",
        default_version='v1',
        description="API endpoints for the Collaborative Task Manager Modular Monolith",
        contact=openapi.Contact(email="admin@school.ac.ke"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# 2. Wire up all your modules
urlpatterns = [
    path('admin/', admin.site.urls),

    # --- 🏗️ Core Modules ---
    path('api/users/', include('users.urls')),
    path('api/academic/', include('academic.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/notifications/', include('comments_notifications.urls')),

    # --- 🔐 Auth & Documentation ---
    path('api-auth/', include('rest_framework.urls')),  # Standard DRF login
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]