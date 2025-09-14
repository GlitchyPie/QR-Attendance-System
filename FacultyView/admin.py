from django.contrib import admin

# Register your models here.

from .models import Student, ClassName, Attendance

admin.site.register(Student)
admin.site.register(ClassName)
admin.site.register(Attendance)