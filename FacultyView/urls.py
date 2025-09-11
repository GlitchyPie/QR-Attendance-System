from . import views
from django.urls import path

urlpatterns = [
    path("", views.faculty_view, name="faculty_view"),
    path("class/<int:classId>/", views.faculty_view_class_id, name="faculty_view_class_id"),
    path("class/<str:className>/", views.faculty_view_class_name, name="faculty_view_class_name"),
    #path("add_manually/class/<str:className>", views.add_manually_class, name="add_manually_class"),
    #path("add_manually/<str:branch>/<str:section>/<int:year>/",views.add_manually_filtered, name="add_manually_filtered"),
    #path("add_manually/<str:branch>/<str:section>/",views.add_manually_filtered_2, name="add_manually_filtered_2"),
    #path("add_manually/<str:branch>/",views.add_manually_filtered_3, name="add_manually_filtered_3"),
]
