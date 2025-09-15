from . import views
from django.urls import path

urlpatterns = [
    path("", views.faculty_view, name="faculty_view"),
    path("class/create/", views.faculty_view_create_class, name="faculty_view_create_class"),
    
    path("class/<int:classId>/<str:action>/<int:year>/<int:month>/<int:day>/", views.faculty_view_attendance_export_id, name="faculty_view_attendance_export_id"),
    path("class/<str:className>/<str:action>/<int:year>/<int:month>/<int:day>/", views.faculty_view_attendance_export_name, name="faculty_view_attendance_export_name"),
    
    path("class/<int:classId>/export/",views.faculty_view_attendance_export_form, name="faculty_view_attendance_export_form"),
    
    path("class/<int:classId>/ajax/present/", views.faculty_view_ajax_present_id, name="faculty_view_ajax_present_id"),
    path("class/<str:className>/ajax/present/", views.faculty_view_ajax_present_name, name="faculty_view_ajax_present_name"),   
    
    path("class/<int:classId>/", views.faculty_view_class_id, name="faculty_view_class_id"),
    path("class/<str:className>/", views.faculty_view_class_name, name="faculty_view_class_name"),
]
