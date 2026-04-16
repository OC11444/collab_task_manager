from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include URLs for the comments and notifications API
    path('api/', include('comments_notifications.urls')),
]