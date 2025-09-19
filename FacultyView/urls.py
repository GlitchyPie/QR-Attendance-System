from . import views
from django.urls import path, include

attendanceUrls = [
    path("", views.faculty_view_attendance_export),
    path("today/", views.faculty_view_attendance_export, name="faculty_view_attendance"),
    path("attendance/today/<str:action>/", views.faculty_view_attendance_export, name="faculty_view_attendance"),
    path("<int:year>/<int:month>/<int:day>/", views.faculty_view_attendance_export, name="faculty_view_attendance"),
    path("<int:year>/<int:month>/<int:day>/<str:action>/", views.faculty_view_attendance_export, name="faculty_view_attendance"),
]
presentListUrls = [
    path("", views.faculty_view_present_list),
    path("today/", views.faculty_view_present_list, name="faculty_view_present_list"),
    path("<int:year>/<int:month>/<int:day>/", views.faculty_view_present_list, name="faculty_view_present_list")
]

urlpatterns = [
    path("", views.faculty_view, name="faculty_view"),
    
    path("attendance/", include(attendanceUrls)),
    path("attendance/class/<int:classId>/", include(attendanceUrls)),
    path("attendance/module/<int:moduleId>/", include(attendanceUrls)),
    path("attendance/class/<int:classId>/entry/delete/",views.faculty_view_delete_attendance,name="Faculty_view_delete_attendance"),

    path("present-list/", include(presentListUrls)),
    path("present-list/class/<int:classId>/", include(presentListUrls)),
    path("present-list/module/<int:moduleId>/", include(presentListUrls)),

    path("class/create/", views.faculty_view_create_class, name="faculty_view_create_class"),

    path("class/<int:classId>/", views.faculty_view_class, name="faculty_view_class"),
    path("module/<int:moduleId>/", views.faculty_view, name="faculty_view_module"),

    path("module/<int:moduleId>/class/<str:className>/",views.faculty_view_class, name="faculty_view_class_name"),
    path("module/<str:moduleName>/class/<str:className>/",views.faculty_view_class, name="faculty_view_class_name"),
]