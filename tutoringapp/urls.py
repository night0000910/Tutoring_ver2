from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
    path("reserve/", views.reserve_view, name="reserve"),
    path("choose_reserved_class_datetime/<int:teacher_id>/", views.choose_reserved_class_datetime_view, name="choose_reserved_class_datetime"),
    path("manage_schedule/", views.manage_schedule_view, name="manage_schedule"),
    path("add_teachers_class/<int:year>/<int:month>/<int:day>/<int:hour>/", views.add_teachers_class_view, name="add_teachers_class"),
]