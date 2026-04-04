from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'notifications', NotificationViewSet, basename='notifications')
urlpatterns = [
    path('', include(router.urls)),
]