from django.shortcuts import get_object_or_404, render
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

# ユーザーの詳細情報を取得
class GetUserView(views.APIView):

    permission_class = [permissions.IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        user = get_user_model().objects.get(id=user_id)

        serializer = serializers.UserSerializer(instance=user)

        return Response(serializer.data, status.HTTP_200_OK)

class CreateDummyStudentView(generics.CreateAPIView):
    pass


# ---------------------------生徒専用のAPI----------------------------


# 授業が予約可能な講師を取得する
# UserModelのid=1の行は、ダミーの生徒を表している
class GetTeacherView(views.APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        teachers_set = tutoringapp.models.TeacherModel.objects.all()
        teachers_list = []
        now = timezone.now()

        for teacher in teachers_set:
            teachers_class_set = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id)

            for teachers_class in teachers_class_set:

                if judge_datetime_is_within_oneweek(teachers_class.datetime) and teachers_class.student.user.id == 1: # ClassModelにおいてstudent列の値が1(ダミーの生徒)の授業は、予約されていない授業を表す
                    teachers_list.append({"username" : teacher.user.username, "user_id" : teacher.user.id})
                    break

        return Response(teachers_list, status.HTTP_200_OK)

# 講師の一週間分の、特定の生徒が予約した授業を取得する
class GetWeeklySpecificTeachersReservedClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    # teacher_id : 講師のUserModelにおけるid, student_id : 生徒のUserModelにおけるid
    def get(self, request, *args, **kwargs):
        teacher_id = request.query_params.get("teacher_id")
        student_id = request.query_params.get("student_id")

        teacher = tutoringapp.models.TeacherModel.objects.get(user=teacher_id)
        student = tutoringapp.models.StudentModel.objects.get(user=student_id)

        teachers_class_set = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).filter(student=student.id) # 講師の授業のうち、特定の生徒が予約した授業のセット
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

# クラスの詳細情報を取得する
class GetClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        teacher_id = request.query_params.get("teacher_id")
        teacher = tutoringapp.models.TeacherModel.objects.get(user=teacher_id)

        year = int(request.query_params.get("year")) # JSTとして日時を取得する
        month = int(request.query_params.get("month"))
        day = int(request.query_params.get("day"))
        hour = int(request.query_params.get("hour"))
        time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
        time -= datetime.timedelta(hours=9) # JSTをUTCに変換

        teachers_class = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).get(datetime=time)
        serializer = serializers.ClassSerializer(instance=teachers_class)

        return Response(serializer.data, status.HTTP_200_OK)

# 生徒がクラスを予約する
class AddReservedClassView(views.APIView):

    permission_class = [permissions.IsAuthenticated]

    def patch(self, request, class_id, *args, **kwargs):

        user = request.user
        student = tutoringapp.models.StudentModel.objects.get(user=user.id)

        teachers_class = get_object_or_404(tutoringapp.models.ClassModel, id=class_id)
        serializer = serializers.ClassSerializer(instance=teachers_class, data={"student" : student.id}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)


# ---------------------------講師関連のAPI----------------------------


# 今日行う授業を取得する
class GetDailyTeachersReservedClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        teacher = tutoringapp.models.TeacherModel.objects.get(user=user.id)

        teachers_class_set = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).exclude(student=1)
        teachers_class_list = change_set_to_list(teachers_class_set)
        weekly_teachers_class_list = []

        jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) # JSTにおける0時0分
        today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
        zero_oclock = 0
        fifteen_oclock = 15
        twenty_four_oclock = 24

        for j in range(fifteen_oclock, twenty_four_oclock):
            added_datetime = today.replace(hour=j)
            print(added_datetime)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class:
                weekly_teachers_class_list.append(duplicate_class)

        for j in range(zero_oclock, fifteen_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=1)
            print(added_datetime)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class:
                weekly_teachers_class_list.append(duplicate_class)
        
        serializer = serializers.ClassSerializer(instance=weekly_teachers_class_list, many=True)
        weekly_teachers_class_list = serializer.data

        for i, weekly_teachers_class in enumerate(weekly_teachers_class_list):

            class_datetime = weekly_teachers_class.pop("datetime") # class_datetime変数には、ISO8601に則って表記された日時の文字列が格納されている
            class_datetime_list = class_datetime.split("T")
            date = class_datetime_list[0] # 日付を表す文字列
            time = class_datetime_list[1] # 時刻を表す文字列
            time = time.split("+")[0]

            date_list = date.split("-")
            year = int(date_list[0])
            month = int(date_list[1])
            day = int(date_list[2])

            time_list = time.split(":")
            hour = int(time_list[0])

            weekly_teachers_class_list[i]["year"] = year
            weekly_teachers_class_list[i]["month"] = month
            weekly_teachers_class_list[i]["day"] = day
            weekly_teachers_class_list[i]["hour"] = hour

        return Response(serializer.data, status.HTTP_200_OK)

# 講師の一週間分の、生徒が予約した授業を取得する
class GetWeeklyTeachersReservedClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        teacher = tutoringapp.models.TeacherModel.objects.get(user=user.id)

        teachers_class_set = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).exclude(student=1)
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
        
        serializer = serializers.ClassSerializer(instance=weekly_teachers_class_list, many=True)
        weekly_teachers_class_list = serializer.data

        for i, weekly_teachers_class in enumerate(weekly_teachers_class_list):

            class_datetime = weekly_teachers_class.pop("datetime") # class_datetime変数には、ISO8601に則って表記された日時の文字列が格納されている
            class_datetime_list = class_datetime.split("T")
            date = class_datetime_list[0] # 日付を表す文字列
            time = class_datetime_list[1] # 時刻を表す文字列
            time = time.split("+")[0]

            date_list = date.split("-")
            year = int(date_list[0])
            month = int(date_list[1])
            day = int(date_list[2])

            time_list = time.split(":")
            hour = int(time_list[0])

            weekly_teachers_class_list[i]["year"] = year
            weekly_teachers_class_list[i]["month"] = month
            weekly_teachers_class_list[i]["day"] = day
            weekly_teachers_class_list[i]["hour"] = hour

        return Response(serializer.data, status.HTTP_200_OK)


# 講師の一週間分の授業を取得する
class GetWeeklyTeachersClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    # teacher_id : 講師のUserModelにおけるid, student_id : 生徒のUserModelにおけるid
    def get(self, request, teacher_id, *args, **kwargs):

        teacher = tutoringapp.models.TeacherModel.objects.get(user=teacher_id)

        teachers_class_set = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id) # 講師が登録した全ての授業のセット
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
class AddTeachersClassView(views.APIView):

    permission_class = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        user = request.user
        teacher = tutoringapp.models.TeacherModel.objects.get(user=user.id)
        year = int(request.data.get("year")) # JSTとして日時を取得する
        month = int(request.data.get("month"))
        day = int(request.data.get("day"))
        hour = int(request.data.get("hour"))
        time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
        time -= datetime.timedelta(hours=9) # JSTをUTCに変換
        time_text = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        serializer = serializers.ClassSerializer(data={"student" : 1, "teacher" : teacher.id, "datetime" : time_text})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)

