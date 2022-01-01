from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from . import views


urlpatterns = [
    path("login/", views.LoginView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("users/<user_id>/", views.GetUserView.as_view()), # ユーザーの詳細情報を取得する
    path("classes/non_reserved_classes/teachers/", views.GetTeachersView.as_view()), # 授業が予約可能な講師を取得する
    path("classes/weekly_classes/", views.GetWeeklySpecificTeachersReservedClassView.as_view()), # 講師の一週間分の、特定の生徒が予約した授業を取得する
    path("classes/", views.GetClassView.as_view()), # クラスの詳細情報を取得する
    path("classes/<class_id>/", views.AddReservedClassView.as_view()), # 生徒がクラスを予約する
    path("users/authenticated_teacher/classes/daily_classes/reserved_classes/", views.GetDailyTeachersReservedClassView.as_view()), # 今日行う授業のうち、残りの授業を取得する
    path("users/authenticated_teacher/classes/weekly_classes/reserved_classes/", views.GetWeeklyTeachersReservedClassView.as_view()), # 講師の一週間分の、生徒が予約した授業を取得する
    path("users/<teacher_id>/classes/weekly_classes/", views.GetWeeklyTeachersClassView.as_view()), # 講師の一週間分の授業を取得する
    path("users/authenticated_teacher/classes/", views.AddTeachersClassView.as_view()), # 講師が授業を登録する
]
