from . import views
from django.urls import path

urlpatterns = [
    path("", views.faculty_view, name="faculty_view"),
    path("class/create/", views.faculty_view_create_class, name="faculty_view_create_class"),   
    path("class/<int:classId>/", views.faculty_view_class_id, name="faculty_view_class_id"),
    path("class/<str:className>/", views.faculty_view_class_name, name="faculty_view_class_name"),
]
