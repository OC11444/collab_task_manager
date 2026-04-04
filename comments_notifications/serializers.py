from rest_framework import serializers
from .models import Comment, Notification


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at']
        read_only_fields = ('id', 'author', 'created_at')


class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'task',
            'message',
            'notification_type',
            'is_read',
            'created_at'
        ]
        read_only_fields = ('id', 'recipient', 'created_at')