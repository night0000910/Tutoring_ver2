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

# UTCをJSTに変換する
# 引数には、UTCとしての日付、時刻を受け取る
def change_utc_to_jst(year, month, day, hour):

    time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    time += datetime.timedelta(hours=9) # JSTをUTCに変換

    year = time.year
    month = time.month
    day = time.day
    hour = time.hour

    return (year, month, day, hour)

# JSTをUTCに変換する
# 引数には、JSTとしての日付、時刻を受け取る
def change_jst_to_utc(year, month, day, hour):

    time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
    time -= datetime.timedelta(hours=9) # JSTをUTCに変換

    year = time.year
    month = time.month
    day = time.day
    hour = time.hour

    return (year, month, day, hour)

def serialize_class_list(class_list):

    serializer = serializers.ClassSerializer(instance=class_list, many=True) # この処理において、UTCはJSTへ変換される
    class_list = serializer.data

    for i, specific_class in enumerate(class_list):

        class_datetime = specific_class.pop("datetime") # class_datetime変数には、ISO8601に則って表記されたJSTにおける日時の文字列が格納されている
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

        class_list[i]["year"] = year
        class_list[i]["month"] = month
        class_list[i]["day"] = day
        class_list[i]["hour"] = hour

        student_id = specific_class.pop("student") # student_idは、生徒のStudentModelにおけるid
        teacher_id = specific_class.pop("teacher") # teacher_idは、講師のTeacherModelにおけるid

        student = tutoringapp.models.StudentModel.objects.get(id=student_id)
        student = student.user
        student_id = student.id # student_idをUserModelにおけるidに更新
        teacher = tutoringapp.models.TeacherModel.objects.get(id=teacher_id)
        teacher = teacher.user
        teacher_id = teacher.id # teacher_idをUserModelにおけるidに更新

        class_list[i]["student_id"] = student_id
        class_list[i]["teacher_id"] = teacher_id
    
    return class_list

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

# ユーザーの詳細情報を取得する
class GetUserView(views.APIView):

    permission_class = [permissions.IsAuthenticated]

    # user_id : ユーザーのUserModelにおけるid
    def get(self, request, user_id, *args, **kwargs):
        user = get_user_model().objects.get(id=user_id)

        serializer = serializers.UserSerializer(instance=user)

        return Response(serializer.data, status.HTTP_200_OK)

class CreateDummyStudentView(generics.CreateAPIView):
    pass


# ---------------------------生徒専用のAPI----------------------------


# 授業が予約可能な講師を取得する
# UserModelのid=1の行は、ダミーの生徒を表している
class GetTeachersView(views.APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        teachers_set = tutoringapp.models.TeacherModel.objects.all()
        teachers_list = []
        now = timezone.now()

        for teacher in teachers_set:
            teachers_class_set = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id)

            for teachers_class in teachers_class_set:

                if judge_datetime_is_within_oneweek(teachers_class.datetime) and teachers_class.student.user.id == 1: # ClassModelにおいてstudent列の値が1(ダミーの生徒)の授業は、予約されていない授業を表す
                    teacher = teacher.user # TeacherModelからUserModelへ変換
                    teachers_list.append(teacher)
                    break
        
        serializer = serializers.UserSerializer(instance=teachers_list, many=True)
        teachers_list = serializer.data

        return Response(teachers_list, status.HTTP_200_OK)

# 特定の生徒が予約した授業を取得する(ただし、現在時刻より前の授業は取得されない)
class GetDailySpecificReservedClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    # teacher_id : 講師のUserModelにおけるid, student_id : 生徒のUserModelにおけるid
    def get(self, request, *args, **kwargs):

        user = request.user
        student = tutoringapp.models.StudentModel.objects.get(user=user.id)

        reserved_class_set = tutoringapp.models.ClassModel.objects.filter(student=student.id) # 特定の生徒が予約した授業のセット
        reserved_class_list = change_set_to_list(reserved_class_set)
        daily_reserved_class_list = []

        jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) # JSTにおける0時0分
        today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
        now = timezone.now().replace(minute=0, second=0, microsecond=0) # UTCにおける現在時刻(ただし、分、秒、マイクロ秒は0)
        zero_oclock = 0
        fifteen_oclock = 15
        twenty_four_oclock = 24

        for j in range(fifteen_oclock, twenty_four_oclock):
            added_datetime = today.replace(hour=j)
            duplicate_class = return_datetime_duplicate_class(reserved_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class and added_datetime.timestamp() >= now.timestamp():
                daily_reserved_class_list.append(duplicate_class)

        for j in range(zero_oclock, fifteen_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=1)
            duplicate_class = return_datetime_duplicate_class(reserved_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class and added_datetime.timestamp() >= now.timestamp():
                daily_reserved_class_list.append(duplicate_class)

        daily_reserved_class_list = serialize_class_list(daily_reserved_class_list) # この処理において、UTCはJSTへ変換される
        
        return Response(daily_reserved_class_list, status.HTTP_200_OK) # 日付、時刻はJSTとして返す

# 講師の一週間分の、特定の生徒が予約した授業を取得する(ただし、現在時刻より前の授業は取得されない)
class GetWeeklySpecificReservedClassView(views.APIView):

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
        now = timezone.now().replace(minute=0, second=0, microsecond=0) # UTCにおける現在時刻(ただし、分、秒、マイクロ秒は0)
        zero_days_after = 0
        seven_days_after = 7
        zero_oclock = 0
        fifteen_oclock = 15
        twenty_four_oclock = 24

        for i in range(zero_days_after, seven_days_after):

            for j in range(fifteen_oclock, twenty_four_oclock):
                added_datetime = today.replace(hour=j) + datetime.timedelta(days=i)
                duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

                if duplicate_class and added_datetime.timestamp() >= now.timestamp():
                    weekly_teachers_class_list.append(duplicate_class)

            for j in range(zero_oclock, fifteen_oclock):
                added_datetime = today.replace(hour=j) + datetime.timedelta(days=i+1)
                duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

                if duplicate_class and added_datetime.timestamp() >= now.timestamp():
                    weekly_teachers_class_list.append(duplicate_class)

        weekly_teachers_class_list = serialize_class_list(weekly_teachers_class_list) # この処理において、UTCはJSTへ変換される
        
        return Response(weekly_teachers_class_list, status.HTTP_200_OK) # 日付、時刻はJSTとして返す

# クラスの詳細情報を取得する
# 講師id, 日付、時刻からクラスを特定する
class GetClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        teacher_id = request.query_params.get("teacher_id") # 講師のUserModelにおけるid
        teacher = tutoringapp.models.TeacherModel.objects.get(user=teacher_id)

        year = int(request.query_params.get("year")) # JSTとして日時を取得する
        month = int(request.query_params.get("month"))
        day = int(request.query_params.get("day"))
        hour = int(request.query_params.get("hour"))

        year, month, day, hour = change_jst_to_utc(year, month, day, hour)
        time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)

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


# 今日行う授業のうち、残りの授業を取得する
class GetDailyReservedClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        teacher = tutoringapp.models.TeacherModel.objects.get(user=user.id)

        teachers_class_set = tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).exclude(student=1)
        teachers_class_list = change_set_to_list(teachers_class_set)
        daily_teachers_class_list = []

        jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) # JSTにおける0時0分
        today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
        now = timezone.now().replace(minute=0, second=0, microsecond=0) # UTCにおける現在時刻(ただし、分、秒、マイクロ秒は0)
        zero_oclock = 0
        fifteen_oclock = 15
        twenty_four_oclock = 24

        for j in range(fifteen_oclock, twenty_four_oclock):
            added_datetime = today.replace(hour=j)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class and added_datetime.timestamp() >= now.timestamp():
                daily_teachers_class_list.append(duplicate_class)

        for j in range(zero_oclock, fifteen_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=1)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class and added_datetime.timestamp() >= now.timestamp():
                daily_teachers_class_list.append(duplicate_class)
        
        daily_teachers_class_list = serialize_class_list(daily_teachers_class_list) # この処理において、UTCはJSTへ変換される

        return Response(daily_teachers_class_list, status.HTTP_200_OK)

# 講師の一週間分の、生徒が予約した授業を取得する
class GetWeeklyReservedClassView(views.APIView):

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
                duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

                if duplicate_class:
                    weekly_teachers_class_list.append(duplicate_class)

            for j in range(zero_oclock, fifteen_oclock):
                added_datetime = today.replace(hour=j) + datetime.timedelta(days=i+1)
                duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

                if duplicate_class:
                    weekly_teachers_class_list.append(duplicate_class)
        
        weekly_teachers_class_list = serialize_class_list(weekly_teachers_class_list) # この処理において、UTCはJSTへ変換される

        return Response(weekly_teachers_class_list, status.HTTP_200_OK)


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
                duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

                if duplicate_class:
                    weekly_teachers_class_list.append(duplicate_class)

            for j in range(zero_oclock, fifteen_oclock):
                added_datetime = today.replace(hour=j) + datetime.timedelta(days=i+1)
                duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

                if duplicate_class:
                    weekly_teachers_class_list.append(duplicate_class)
        

        for weekly_teachers_class in weekly_teachers_class_list:
            print(weekly_teachers_class.datetime)

        weekly_teachers_class_list = serialize_class_list(weekly_teachers_class_list) # この処理において、UTCはJSTへ変換される
        
        return Response(weekly_teachers_class_list, status.HTTP_200_OK)

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

        year, month, day, hour = change_jst_to_utc(year, month, day, hour)
        time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
        time_text = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        serializer = serializers.ClassSerializer(data={"student" : 1, "teacher" : teacher.id, "datetime" : time_text})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)

