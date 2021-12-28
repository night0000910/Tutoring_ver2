from django.shortcuts import render
from django.shortcuts import render, redirect


# -------------------------講師・生徒共通のページ-------------------------


# ホームページ
def home_page_view(request):
    
    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")

        elif user.user_type == "teacher":
            return redirect("manage_schedule")

    else:
        
        return render(request, "home_page.html")

# ログインページ
def login_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")

        elif user.user_type == "teacher":
            return redirect("manage_schedule")

    else:
        
        return render(request, "login.html")


# ---------------------------生徒専用のページ----------------------------


def reserve_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return render(request, "reserve.html")
        
        elif user.user_type == "teacher":
            return redirect("manage_schedule")
    
    else:

        return redirect("home_page")

def choose_reserved_class_datetime_view(request, teacher_id):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return render(request, "choose_reserved_class_datetime.html", {"teacher_id" : teacher_id})
        
        elif user.user_type == "teacher":
            return redirect("manage_schedule")
    
    else:

        return redirect("home_page")


# ---------------------------講師専用のページ----------------------------


# 今日行う予定の授業を表示
# 一週間分の授業の予約画面を表示
def manage_schedule_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")
        
        elif user.user_type == "teacher":
            return render(request, "manage_schedule.html")
    
    else:

        return redirect("home_page")

# スケジュールを更新する
def add_teachers_class_view(request, year, month, day, hour):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")
        
        elif user.user_type == "teacher":
            return render(request, "add_teachers_class.html", {"year" : year, "month" : month, "day" : day, "hour" : hour})
    
    else:

        return redirect("home_page")