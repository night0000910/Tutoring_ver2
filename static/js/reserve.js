$(document).ready(function() {

    displayReservedClass()
    displayTeachers()
})

function displayReservedClass(){
    var request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/api/v1/users/authenticated_student/classes/daily_classes/");
    request.onload = createElementsOfReservedClass;
    request.send();
}
function createElementsOfReservedClass(){
    response = JSON.parse(this.response);
    console.log(response);
}

function displayTeachers(){
    var request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/api/v1/classes/non_reserved_classes/teachers/");
    request.onload = createElementsOfTeachers;
    request.send();
}

function createElementsOfTeachers(){
    var response = JSON.parse(this.response);
    console.log(response);

    var ul = document.getElementById("teacher-container");

    for (var teacher of response){
        var teacherId = teacher.id;
        var firstName = teacher.first_name;
        var lastName = teacher.last_name;
        var profileImage = teacher.profile_image;

        var li = document.createElement("li");
        li.setAttribute("class", "collection-item avatar");
        var a = document.createElement("a");
        a.setAttribute("href", "http://127.0.0.1:8000/tutoring/choose_reserved_class_datetime/" + teacherId + "/");
        var img = document.createElement("img");
        img.setAttribute("src", profileImage);
        img.setAttribute("alt", "");
        img.setAttribute("class", "circle");
        var span = document.createElement("span");
        span.setAttribute("class", "title");
        span.innerHTML = lastName + " " + firstName;

        li.appendChild(a);
        a.appendChild(img);
        a.appendChild(span);
        ul.appendChild(li);
    }

}

