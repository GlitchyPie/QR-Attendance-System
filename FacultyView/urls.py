from . import views
from django.urls import path, include

attendanceUrlSuffixes=[
    path('', views.faculty_view_attendance_export),
    path('today/', views.faculty_view_attendance_export, name='faculty_view_attendance'),
    path('today/<str:action>/', views.faculty_view_attendance_export, name='faculty_view_attendance'),
    path('<int:year>/<int:month>/<int:day>/', views.faculty_view_attendance_export, name='faculty_view_attendance'),
    path('<int:year>/<int:month>/<int:day>/<str:action>/', views.faculty_view_attendance_export, name='faculty_view_attendance'),
]
attendanceUrls = [
    path('', include(attendanceUrlSuffixes)),
    path('class/<int:classId>/', include(attendanceUrlSuffixes)),
    path('module/<int:moduleId>/', include(attendanceUrlSuffixes)),
    path('entry/delete/', views.faculty_view_delete_attendance, name='faculty_view_delete_attendance'),
]


presentListUrlSuffixess = [
    path('', views.faculty_view_present_list),
    path('today/', views.faculty_view_present_list, name='faculty_view_present_list'),
    path('<int:year>/<int:month>/<int:day>/', views.faculty_view_present_list, name='faculty_view_present_list')
]
presentListUrls = [
    path('', include(presentListUrlSuffixess)),
    path('class/<int:classId>/',include(presentListUrlSuffixess)),
    path('module/<int:moduleId>/',include(presentListUrlSuffixess)),
]

classUrls = [
    path('create', views.faculty_view_create_class, name='faculty_view_create_class'),
    path('<int:classId>/', views.faculty_view, name='faculty_view'),
]

modulePaths = [
    path('<int:moduleId>/', views.faculty_view, name='faculty_view'),
    path('<int:moduleId>/class/<str:className>/',views.faculty_view, name='faculty_view'),
    path('<str:moduleName>/class/<str:className>/',views.faculty_view, name='faculty_view'),
]

urlpatterns = [
    path('', views.faculty_view, name='faculty_view'),
    
    path('attendance/', include(attendanceUrls)),

    path('present-list/', include(presentListUrls)),

    path('class/', include(classUrls)),

    path('module/',include(modulePaths)),   
]