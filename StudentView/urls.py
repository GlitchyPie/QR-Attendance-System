from . import views
from django.urls import path

urlpatterns = [
    path("class/<int:classId>/attendance/entry/",views.student_view_name_entry,name="student_view_name_entry_by_class_id"),
    path("class/<int:classId>/attendance/submit/",views.student_view_submit_attendance,name="student_view_submit_attendance_by_class_id"),

    path("class/<str:className>/attendance/entry/",views.student_view_name_entry,name="student_view_name_entry_by_class_name"),
    path("class/<str:className>/attendance/submit/",views.student_view_submit_attendance,name="student_view_submit_attendance_by_class_name"),
    
    path("attendance/submitted/<int:classId>", views.student_view_attendance_submitted, name="student_view_attendance_submitted_with_classId"),
    path("attendance/submitted/<str:className>", views.student_view_attendance_submitted, name="student_view_attendance_submitted_with_className"),
    path("attendance/submitted", views.student_view_attendance_submitted, name="student_view_attendance_submitted_with_classId"),
    
    path("attendance/already-submitted/<int:classId>", views.student_view_attendance_already_submitted, name="student_view_attendance_already_submitted_with_classId"),
    path("attendance/already-submitted/<str:className>", views.student_view_attendance_already_submitted, name="student_view_attendance_already_submitted_with_className"),
    path("attendance/already-submitted", views.student_view_attendance_already_submitted, name="student_view_attendance_already_submitted"),

    path("class/<int:classId>/qr-code-<int:blockSize>/",views.student_view_bigQRcode,name="student_view_qrCode_with_blockSize"),
    path("class/<int:classId>/qr-code/",views.student_view_bigQRcode,name="student_view_qrCode"),
    
    path("class/<str:className>/qr-code-<int:blockSize>/",views.student_view_bigQRcode,name="student_view_qrCode_with_blockSize"),
    path("class/<str:className>/qr-code/",views.student_view_bigQRcode,name="student_view_qrCode")
]
