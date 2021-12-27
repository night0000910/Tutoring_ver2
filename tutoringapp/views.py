from django.shortcuts import render
from django.shortcuts import render, redirect


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

def login_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")

        elif user.user_type == "teacher":
            return redirect("manage_schedule")

    else:
        
        return render(request, "login.html")

def manage_schedule_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reverse")
        
        elif user.user_type == "teacher":
            return render(request, "manage_schedule.html")
    
    else:

        return redirect("home_page")

def add_teachers_class_view(request, year, month, day, hour):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reverse")
        
        elif user.user_type == "teacher":
            return render(request, "add_teachers_class.html", {"year" : year, "month" : month, "day" : day, "hour" : hour})
    
    else:

        return redirect("home_page")