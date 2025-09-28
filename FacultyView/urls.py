from . import views
from django.urls import path, include
from django.views.generic.base import RedirectView


attendanceUrlSuffixes=[
    #Redirects==
    path('', RedirectView.as_view(url='today/view/', permanent=False)),
    path('today/', RedirectView.as_view(url='view/', permanent=False)),
    path('<int:year>/', RedirectView.as_view(url='view/', permanent=False)),
    path('<int:year>/<int:month>/', RedirectView.as_view(url='view/', permanent=False)),
    path('<int:year>/<int:month>/<int:day>/', RedirectView.as_view(url='view/', permanent=False)),
    
    #Actual=====
    path('today/<str:action>/', views.faculty_view_attendance_view_today, name='faculty_view_attendance'),
    path('<int:year>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
    path('<int:year>/<int:month>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
    path('<int:year>/<int:month>/<int:day>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),

    path('from/<int:year_start>-<int:month_start>-<int:day_start>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
    path('to/<int:year_end>-<int:month_end>-<int:day_end>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
    path('from/<int:year_start>-<int:month_start>-<int:day_start>/to/<int:year_end>-<int:month_end>-<int:day_end>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
]


attendanceUrls = [
    path('', include(attendanceUrlSuffixes)),
    path('class/<int:classId>/', include(attendanceUrlSuffixes)),
    path('module/<int:moduleId>/', include(attendanceUrlSuffixes)),

    path('entry/delete/', views.faculty_view_delete_attendance, name='faculty_view_delete_attendance'),
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

    path('class/', include(classUrls)),

    path('module/',include(modulePaths)),   
]