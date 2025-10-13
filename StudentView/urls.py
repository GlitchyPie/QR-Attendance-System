from . import views
from django.urls import path, re_path, include

ATTENDANCE_PATHS = [
    path('registration/',views.student_view_registration_form,name='student_view_registration_form'),
    path('submit/',views.student_view_submit_attendance,name='student_view_submit_attendance'),
    path('submit/ajax/',views.student_view_submit_attendance_ajax,name='student_view_submit_attendance_ajax'),
    path('submitted/', views.student_view_attendance_submitted, name='student_view_attendance_submitted'),
    path('already-submitted/', views.student_view_attendance_submitted, name='student_view_attendance_already_submitted'),
]

QR_CODE_PATHS = [
    path('print/',views.student_view_print_qrCode,name='student_view_print_qrCode'),
    path('print/boxsize-<int:boxSize>/',views.student_view_print_qrCode,name='student_view_print_qrCode'),
    
    path('image/',views.student_view_qrCode_image, name='student_view_qrCode_image'),
    path('image/boxsize-<int:boxSize>/',views.student_view_qrCode_image, name='student_view_qrCode_image'),

    re_path(r'^image/.(?P<extension>[a-z0-9]+)/$',views.student_view_qrCode_image, name='student_view_qrCode_image'),
    re_path(r'^image/boxsize-(?P<boxSize>[0-9]+)/\.(?P<extension>[a-z0-9]+)/$',views.student_view_qrCode_image, name='student_view_qrCode_image'),
]


urlpatterns = [
    path('attendance/class/<int:classId>/', include(ATTENDANCE_PATHS)),
    
    path('lookup/', views.student_view_student_lookup, name='student_view_student_lookup'),

    path('qr-code/<int:classId>/', include(QR_CODE_PATHS)),
]
