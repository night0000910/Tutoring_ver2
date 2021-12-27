$(document).ready(function() {
    addClassButton = document.getElementById("add-class-btn");
    notAddClassButton = document.getElementById("not-add-class-btn");
    console.log(notAddClassButton);

    addClassButton.addEventListener("click", addClass);
    notAddClassButton = document.getElementById("click", displayManageSchedule);
})

function addClass(){
    userId = Number(document.getElementById("user-id").getAttribute("value"));
    dummy_student_id = 1
    year = document.getElementById("year").getAttribute("value");
    month = document.getElementById("month").getAttribute("value") - 1; /* Dateオブジェクトは月の値を0~11として扱うため */
    day = document.getElementById("day").getAttribute("value");
    hour = document.getElementById("hour").getAttribute("value"); /* UTCとJSTの間には9時間分の時差があるため */
    datetime = new Date(year, month, day, hour);
    datetime_text = datetime.toISOString();

    teachers_class = {student : dummy_student_id, teacher : userId, datetime : datetime_text};
    json = JSON.stringify(teachers_class);
    console.log(json);

    csrfToken = getCsrfToken()

    request = new XMLHttpRequest()
    request.open("POST", "http://127.0.0.1:8000/api/v1/users/authenticated_teacher/classes/");
    request.setRequestHeader("Content-type", "application/json");
    request.setRequestHeader("X-CSRFToken", csrfToken);
    request.onload = displayManageSchedule
    request.send(json);
}

function displayManageSchedule(){

    window.location.href = "http://127.0.0.1:8000/tutoring/manage_schedule/";

}

function getCsrfToken(){
    cookies = document.cookie;
    cookiesArray = cookies.split(";");

    for (cookie of cookiesArray){
        cookieArray = cookie.split("=");

        if (cookieArray[0] == "csrftoken"){
            csrfToken = cookieArray[1];
        }
    }

    return csrfToken
}