from django.shortcuts import render
from django.contrib.auth import login, logout
from django.utils import timezone
from rest_framework import status, views
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

import datetime

from . import serializers
import tutoringapp.models


# 行のセットをリストに変換する
def change_set_to_list(record_set):

    record_list = []

    for record in record_set:
        record_list.append(record)
    
    return record_list

# 重複した時刻の授業を返す
def return_datetime_duplicate_class(class_list, year, month, day, hour):

    duplicate_class = None

    for this_class in class_list:

        if this_class.datetime.year == year and this_class.datetime.month == month and this_class.datetime.day == day and this_class.datetime.hour == hour:
            duplicate_class = this_class
    
    return duplicate_class


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

class GetTeachersClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        user = request.user
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

class AddTeachersClassView(generics.CreateAPIView):

    queryset = tutoringapp.models.TeacherModel.objects.all()
    serializer_class = serializers.TeachersClassSerializer

