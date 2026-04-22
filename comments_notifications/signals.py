"""
Module: comments_notifications
Author: OC11444

Defines our custom event broadcaster. We use signals so other apps in our monolith can react to a new comment without being tightly coupled to this specific module.
"""
from django.dispatch import Signal

# This is the 'frequency' that tasks/signals.py is tuning into
comment_created = Signal()