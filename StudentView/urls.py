from . import views
from django.urls import path, include

attendanceUrls = [
    path('entry/',views.student_view_name_entry,name='student_view_enter_student'),
    path('submit/',views.student_view_submit_attendance,name='student_view_submit_attendance'),
    path('submit/ajax/',views.student_view_submit_attendance_ajax,name='student_view_submit_attendance_ajax'),
    path('submitted/', views.student_view_attendance_submitted, name='student_view_attendance_submitted'),
    path('already-submitted/', views.student_view_attendance_submitted, name='student_view_attendance_already_submitted'),
]

urlpatterns = [
    path('attendance/class/<int:classId>/', include(attendanceUrls)),
    
    path('student/lookup/', views.student_view_student_lookup, name='student_view_student_lookup'),

    path('qr-code/class/<int:classId>/blocksize-<int:blockSize>/',views.student_view_bigQRcode,name='student_view_qrCode'),
    path('qr-code/class/<int:classId>/',views.student_view_bigQRcode,name='student_view_qrCode'),
]
