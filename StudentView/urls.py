from . import views
from django.urls import path, re_path

urlpatterns = [
    path("attendance/class/<int:classId>/entry/",views.student_view_name_entry,name="student_view_enter_student"),
    path("attendance/class/<int:classId>/submit/",views.student_view_submit_attendance,name="student_view_submit_attendance"),
    re_path(r"attendance/(class/(?P<classId>[0-9]+)/)?submitted/", views.student_view_attendance_submitted, name="student_view_attendance_submitted"),
    re_path(r"attendance/(class/(?P<classId>[0-9]+)/)?already-submitted/", views.student_view_attendance_already_submitted, name="student_view_attendance_already_submitted"),
    
    path("qr-code/blocksize-<int:blockSize>/class/<int:classId>/",views.student_view_bigQRcode,name="student_view_qrCode_with_blockSize"),
    path("qr-code/class/<int:classId>/",views.student_view_bigQRcode,name="student_view_qrCode"),
]
