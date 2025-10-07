from . import views
from django.urls import path, include
from django.views.generic.base import RedirectView

DEFAULT_ACTION = 'view/'

ATTENDANCE_HISTORY_SUFFIXES=[
    #Redirects==
    path('', RedirectView.as_view(url='today/' + DEFAULT_ACTION, permanent=False)),
    path('today/', RedirectView.as_view(url=DEFAULT_ACTION, permanent=False)),
    path('<int:year>/', RedirectView.as_view(url=DEFAULT_ACTION, permanent=False)),
    path('<int:year>/<int:month>/', RedirectView.as_view(url=DEFAULT_ACTION, permanent=False)),
    path('<int:year>/<int:month>/<int:day>/', RedirectView.as_view(url=DEFAULT_ACTION, permanent=False)),
    path('from/<int:year_start>-<int:month_start>-<int:day_start>/', RedirectView.as_view(url=DEFAULT_ACTION, permanent=False)),
    path('to/<int:year_end>-<int:month_end>-<int:day_end>/', RedirectView.as_view(url=DEFAULT_ACTION, permanent=False)),
    path('from/<int:year_start>-<int:month_start>-<int:day_start>/to/<int:year_end>-<int:month_end>-<int:day_end>/<str:action>/', RedirectView.as_view(url=DEFAULT_ACTION, permanent=False)),
    
    #Actual=====
    path('today/<str:action>/', views.faculty_view_attendance_view_today, name='faculty_view_attendance'),
    path('<int:year>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
    path('<int:year>/<int:month>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
    path('<int:year>/<int:month>/<int:day>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),

    path('from/<int:year_start>-<int:month_start>-<int:day_start>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
    path('to/<int:year_end>-<int:month_end>-<int:day_end>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
    path('from/<int:year_start>-<int:month_start>-<int:day_start>/to/<int:year_end>-<int:month_end>-<int:day_end>/<str:action>/', views.faculty_view_attendance_view, name='faculty_view_attendance'),
]


ATTENDANCE_HISTORY_PATHS = [
    path('', include(ATTENDANCE_HISTORY_SUFFIXES)),
    path('class/<int:classId>/', include(ATTENDANCE_HISTORY_SUFFIXES)),
    path('module/<int:moduleId>/', include(ATTENDANCE_HISTORY_SUFFIXES)),

    path('delete-entry/', views.faculty_view_delete_attendance, name='faculty_view_delete_attendance'),
]

CLASS_PATHS = [
    path('create', views.faculty_view_create_class, name='faculty_view_create_class'),
    path('<int:classId>/', views.faculty_view, name='faculty_view'),
]

MODULE_PATHS = [
    path('<int:moduleId>/', views.faculty_view, name='faculty_view'),
    path('<int:moduleId>/class/<str:className>/',views.faculty_view, name='faculty_view'),
    path('<str:moduleName>/class/<str:className>/',views.faculty_view, name='faculty_view'),
]

urlpatterns = [
    path('', views.faculty_view, name='faculty_view'),
    
    path('attendance-history/', include(ATTENDANCE_HISTORY_PATHS)),

    path('class/', include(CLASS_PATHS)),

    path('module/',include(MODULE_PATHS)),
]