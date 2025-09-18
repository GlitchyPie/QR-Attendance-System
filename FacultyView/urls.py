from . import views
from django.urls import path

urlpatterns = [
    path("", views.faculty_view, name="faculty_view"),
    path("class/create/", views.faculty_view_create_class, name="faculty_view_create_class"),

    path("class/present-list/", views.faculty_view_present_list, name="faculty_view_present_list_all_classes_today"),
    path("class/present-list/<int:year>/<int:month>/<int:day>/", views.faculty_view_present_list, name="faculty_view_present_list_all_classes_by_ymd"),
    
    path("class/<int:classId>/present-list/<int:year>/<int:month>/<int:day>/", views.faculty_view_present_list, name="faculty_view_present_list_by_class_id_and_ymd"),
    path("class/<int:classId>/present-list/", views.faculty_view_present_list, name="faculty_view_present_list_by_class_id_today"),
    
    path("class/<str:className>/present-list/<int:year>/<int:month>/<int:day>/", views.faculty_view_present_list, name="faculty_view_present_list_by_class_name_and_ymd"),
    path("class/<str:className>/present-list/", views.faculty_view_present_list, name="faculty_view_present_list_by_class_name"),   
    
    path("class/<int:classId>/attendance/<str:action>/<int:year>/<int:month>/<int:day>/", views.faculty_view_attendance_export, name="faculty_view_attendance_export_form_by_class_id_and_ymd"),
    path("class/<str:className>/attendance/<str:action>/<int:year>/<int:month>/<int:day>/", views.faculty_view_attendance_export, name="faculty_view_attendance_export_form_by_class_name_and_ymd"),
    
    path("class/<int:classId>/attendance/delete/",views.faculty_view_delete_attendance,name="Faculty_view_delete_attendance_by_class_id_today"),
    
    path("class/attendance/<str:action>/<int:year>/<int:month>/<int:day>/", views.faculty_view_attendance_export, name="faculty_view_attendance_export_form_all_classes_by_ymd"),
    path("class/<int:classId>/attendance/",views.faculty_view_attendance_export, name="faculty_view_attendance_export_form_by_class_id"),
    path("class/<str:className>/attendance/",views.faculty_view_attendance_export, name="faculty_view_attendance_export_form_by_class_name"),
    
    path("class/attendance/",views.faculty_view_attendance_export, name="faculty_view_attendance_export_form_all_classes_today"),
    path("class/<int:classId>/", views.faculty_view_class, name="faculty_view_by_class_id_today"),
    path("class/<str:className>/", views.faculty_view_class, name="faculty_view_by_class_name_today"),
]
