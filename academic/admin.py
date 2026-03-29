from django.contrib import admin
from .models import School, Department, Course, Unit, Enrollment
#register ur models here
# This tells Django: "Put these tables on the admin dashboard!"
admin.site.register(School)
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Unit)
admin.site.register(Enrollment)