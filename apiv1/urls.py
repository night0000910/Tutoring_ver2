from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from . import views


urlpatterns = [
    path("login/", views.LoginView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("classes/non_reserved_classes/teachers/", views.GetTeacherView.as_view()),
    path("users/<pk>/classes/weekly_classes/", views.GetTeachersClassView.as_view()),
    path("users/authenticated_teacher/classes/", views.AddTeachersClassView.as_view()),
]
