from django.contrib import admin
from .models import Task, TaskSubmission

#register ur models here
admin.site.register(Task)
admin.site.register(TaskSubmission)