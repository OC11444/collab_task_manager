from django.dispatch import Signal

# Sent when a new comment is created.
# Provides the following kwargs:
# - comment: the newly created Comment instance
# - target_object: the object the comment was created against
comment_created = Signal()