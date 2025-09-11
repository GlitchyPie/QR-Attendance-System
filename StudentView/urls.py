from . import views
from django.urls import path

urlpatterns = [
    path("class/<str:className>/student_entry",views.student_entry,name="student_entry"),
    path("class/<str:className>/submit_attendance",views.submit_attendance,name="submit_attendance"),
    path("submitted", views.submitted, name="submitted"),
]
