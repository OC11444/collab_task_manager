from django.dispatch import Signal

# This is the 'frequency' that tasks/signals.py is tuning into
comment_created = Signal()