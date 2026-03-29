from django.contrib import admin
from .models import Comment, Notification

#register ur models here
admin.site.register(Comment)
admin.site.register(Notification)