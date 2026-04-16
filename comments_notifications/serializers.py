from rest_framework import serializers
from django.db.models import Q
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
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

        # RBAC: If the user is a student, filter the replies they can see
        if getattr(user, 'role', '') == 'student':
            replies = replies.filter(Q(author=user) | Q(author__role='lecturer'))

        if replies.exists():
            # Pass the context down so deeply nested replies stay secure
            return CommentSerializer(replies, many=True, context=self.context).data
        return []