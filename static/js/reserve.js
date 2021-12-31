$(document).ready(function() {
    var request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/api/v1/classes/non_reserved_classes/teachers/");
    request.onload = displayTeachers;
    request.send();
})

function displayTeachers(){
    var response = JSON.parse(this.response);

    for (var teacher of response){
        var li = document.createElement("li");
        var div = document.createElement("div");
        div.setAttribute("class", "collapsible-header");
        div.setAttribute("id", teacher.user_id);
        div.setAttribute("onclick", "displayChooseReservedClassDatetime(this)");
        div.innerHTML = '<i class="material-icons">create</i>' + teacher.username

        var ul = document.getElementById("ul");
        li.appendChild(div);
        ul.appendChild(li);
        
    }

}

function displayChooseReservedClassDatetime(div){
    var teacherId = div.getAttribute("id");

    window.location.href = "http://127.0.0.1:8000/tutoring/choose_reserved_class_datetime/" + teacherId + "/";
}