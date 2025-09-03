from . import views
from django.urls import path

urlpatterns = [
    path("", views.faculty_view, name="faculty_view"),
    path("<str:branch>/<str:section>/<int:year>/", views.faculty_view, name="faculty_view_filtered"),
    path("add_manually", views.add_manually, name="add_manually"),
    path("add_manually/<str:branch>/<str:section>/<int:year>/",views.add_manually_year, name="add_manually_filtered")
]
