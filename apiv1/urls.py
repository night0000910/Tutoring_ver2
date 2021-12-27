from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from . import views


urlpatterns = [
    path("login/", views.LoginView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path(""),
]
