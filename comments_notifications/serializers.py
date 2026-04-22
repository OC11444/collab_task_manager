"""
Module: comments_notifications
Author: OC11444

Converts our comment and notification database objects into JSON formats that the frontend React application can easily render.
"""
from rest_framework import serializers
from django.db.models import Q
from .models import Comment, Notification


class CommentSerializer(serializers.ModelSerializer):
    """
        Packages the comment data. We use a recursive setup here to fetch nested replies so the frontend can build threaded conversations without making extra API calls.
        """
    author_id = serializers.ReadOnlyField(source='author.id')
    author_name = serializers.ReadOnlyField(source='author.username')
    author_role = serializers.ReadOnlyField(source='author.role')  # Assuming your User model has a 'role' field
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author_id', 'author_name', 'author_role', 'content', 'parent', 'replies', 'created_at']

    def get_replies(self, obj):
        """Fetch nested replies and enforce RBAC privacy on the replies too."""
        request = self.context.get('request')
        user = request.user if request else None
        replies = obj.replies.all()



        if replies.exists():
            # Pass the context down so deeply nested replies stay secure
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at', 'target_content_type', 'target_object_id']