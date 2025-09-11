from . import views
from django.urls import path

urlpatterns = [
    path("class/<str:className>/student_entry",views.student_entry_name,name="student_entry_name"),
    path("class/<str:className>/submit_attendance",views.submit_attendance_name,name="submit_attendance_name"),
    path("class/<int:classId>/student_entry",views.student_entry_id,name="student_entry_id"),
    path("class/<int:classId>/submit_attendance",views.submit_attendance_id,name="submit_attendance_id"),  
    path("submitted", views.submitted, name="submitted"),
]
