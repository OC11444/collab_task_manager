"""
Module: comments_notifications
Author: OC11444

Defines the database tables for our messaging and alert system. We use Django's GenericForeignKey here so we can attach comments and notifications to any object in the system without writing new tables for every single feature.
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comment(models.Model):
    """
        Stores discussion threads. We implemented soft deletes here so if an admin removes a bad comment, it just hides it instead of breaking the entire database tree of replies.
        """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    # Polymorphic target (e.g., Task, TaskSubmission)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Security & Audit Enhancement: Soft Deletes
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']



    #class Meta:
        #ordering = ['-created_at']  # newest comments first

    def __str__(self):
        target = self.content_object.__class__.__name__ if self.content_object else "Object"
        status = " (Deleted)" if not self.is_active else ""
        return f"Comment by {self.author} on {target}{status}"


class Notification(models.Model):
    """
        Keeps track of user alerts. We link the notification directly to the target object so the frontend knows exactly which page to load when the user clicks the alert.
        """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    # 🚀 NEW: title acts as the "Actor" (e.g., "Sarah") while message is the "Action"
    title = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)

    # Security Enhancement: Contextual Routing
    # Allows the frontend to securely fetch the related object via RBAC-protected endpoints
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    target_object_id = models.PositiveBigIntegerField(null=True, blank=True)
    target_object = GenericForeignKey('target_content_type', 'target_object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient} - Read: {self.is_read}"