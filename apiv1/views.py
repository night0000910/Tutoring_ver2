from django.shortcuts import render
from django.contrib.auth import get_user_model, login, logout
from django.utils import timezone
from rest_framework import status, views
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

import datetime

from . import serializers
import tutoringapp.models


# --------------------------------関数-------------------------------


# 行のセットをリストに変換する
def change_set_to_list(record_set):

    record_list = []

    for record in record_set:
        record_list.append(record)
    
    return record_list

# 引数に渡された時刻が、昨日の15時0分(JSTにおける、今日の0時0分)から一週間以内の時刻かどうかを判定する
def judge_datetime_is_within_oneweek(this_datetime):
    jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
    seven_days_after = today + datetime.timedelta(days=7)

    if today <= this_datetime < seven_days_after:
        return True
    else:
        return False

# 重複した時刻の授業を返す
def return_datetime_duplicate_class(class_list, year, month, day, hour):

    duplicate_class = None

    for this_class in class_list:

        if this_class.datetime.year == year and this_class.datetime.month == month and this_class.datetime.day == day and this_class.datetime.hour == hour:
            duplicate_class = this_class
    
    return duplicate_class


# -------------------------講師・生徒共通のAPI-------------------------


class LoginView(views.APIView):

    def post(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data, context={"request" : request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        
        return Response({"detail" : "ログインに成功しました。"})

class LogoutView(views.APIView):

    def post(self, request, *args, **kwargs):
        logout(request)

        return Response({"detail" : "ログアウトに成功しました。"})


# ---------------------------生徒関連のAPI----------------------------


class CreateDummyStudentView(generics.CreateAPIView):
    pass


# ---------------------------講師関連のAPI----------------------------

# StudentModelのid=1の行は、ダミーの生徒を表している
class GetTeacherView(views.APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        teachers_set = tutoringapp.models.TeacherModel.objects.all()
        teachers_list = []
        now = timezone.now()

        for teacher in teachers_set:
            teachers_class_set = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id)

            for teachers_class in teachers_class_set:

                if judge_datetime_is_within_oneweek(teachers_class.datetime) and teachers_class.student.id == 1: # ClassModelにおいてstudent列の値が1(ダミーの生徒)の授業は、予約されていない授業を表す
                    teachers_list.append({"username" : teacher.user.username, "user_id" : teacher.user.id})
                    break

        return Response(teachers_list, status.HTTP_200_OK)

# 講師の一週間分の授業を取得する
class GetTeachersClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):

        user = get_user_model().objects.get(id=pk)
        teacher = tutoringapp.models.TeacherModel.objects.get(user=user.id)

        teachers_class_set = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id)
        teachers_class_list = change_set_to_list(teachers_class_set)
        weekly_teachers_class_list = []

        jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) # JSTにおける0時0分
        today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
        zero_days_after = 0
        seven_days_after = 7
        zero_oclock = 0
        fifteen_oclock = 15
        twenty_four_oclock = 24

        for i in range(zero_days_after, seven_days_after):

            for j in range(fifteen_oclock, twenty_four_oclock):
                added_datetime = today.replace(hour=j) + datetime.timedelta(days=i)
                print(added_datetime)
                duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

                if duplicate_class:
                    weekly_teachers_class_list.append(duplicate_class)

            for j in range(zero_oclock, fifteen_oclock):
                added_datetime = today.replace(hour=j) + datetime.timedelta(days=i+1)
                print(added_datetime)
                duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

                if duplicate_class:
                    weekly_teachers_class_list.append(duplicate_class)

        datetime_list = []
        for teachers_class in weekly_teachers_class_list:
            year = teachers_class.datetime.year
            month = teachers_class.datetime.month
            day = teachers_class.datetime.day
            hour = teachers_class.datetime.hour
            datetime_list.append({"year" : year, "month" : month, "day" : day, "hour" : hour})
        
        return Response(datetime_list, status.HTTP_200_OK)

# 講師が授業を登録する
class AddTeachersClassView(generics.CreateAPIView):

    permission_class = [permissions.IsAuthenticated]
    queryset = tutoringapp.models.TeacherModel.objects.all()
    serializer_class = serializers.TeachersClassSerializer

