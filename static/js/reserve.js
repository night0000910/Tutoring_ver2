$(document).ready(function() {

    displayReservedClass()
    displayTeachers()
})

function displayReservedClass(){
    var request = new XMLHttpRequest();
    request.open("GET", "/api/v1/users/authenticated_student/classes/daily_classes/");
    request.onload = createElementsOfReservedClass;
    request.send();
}

function createElementsOfReservedClass(){
    response = JSON.parse(this.response);
    console.log(response);

    var ul = document.getElementById("reserved-class-container");

    if (response.length != 0){

        var reservedClassArray = response;
        sortClassArray(response);

        for (var reservedClass of reservedClassArray){

            var teacherId = reservedClass.teacher_id;
            var year = reservedClass.year;
            var month = reservedClass.month;
            var day = reservedClass.day;
            var hour = reservedClass.hour;

            var now = new Date();

            var request = new XMLHttpRequest();
            request.open("GET", "/api/v1/users/" + teacherId + "/", false);
            request.send();

            var response = JSON.parse(request.responseText)
            var teacherFirstName = response.first_name;
            var teacherLastName = response.last_name;
            var teacherImage = response.profile_image;

            var li = document.createElement("li");
            li.setAttribute("class", "collection-item avatar");
            var a = document.createElement("a");
            a.setAttribute("href", "#");
            var img = document.createElement("img");
            img.setAttribute("src", teacherImage);
            img.setAttribute("alt", "");
            img.setAttribute("class", "circle");
            var span = document.createElement("span");
            span.setAttribute("class", "title");
            span.innerHTML = teacherLastName + " " + teacherFirstName;
            var p = document.createElement("p");
            p.innerHTML = "<br>時間 : " + hour + "時00分〜"

            li.appendChild(a);
            a.appendChild(img);
            a.appendChild(span);
            li.appendChild(p);
            
            if (hour == now.getHours() && now.getMinutes() < 50){
                var classButton = document.createElement("a");
                classButton.setAttribute("class", "waves-effect waves-light btn-small");
                classButton.setAttribute("href", "/tutoring/tutoring/");
                classButton.innerHTML = '<i class="material-icons right">border_color</i>授業を開始する'

                li.appendChild(classButton);
            }

            ul = document.getElementById("reserved-class-container");
            ul.appendChild(li);
        }

    } else{
        ul.remove()
        h5 = document.getElementById("daily-reserved-class");
        h5.remove();
    }
}

function sortClassArray(classArray){
    classArray.sort(function (x, y){
        x = new Date(x.year, x.month, x.day, x.hour);
        y = new Date(y.year, y.month, y.day, y.hour);

        return x.getTime() - y.getTime()
    });
}

function displayTeachers(){
    var request = new XMLHttpRequest();
    request.open("GET", "/api/v1/classes/non_reserved_classes/teachers/");
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
        a.setAttribute("href", "/tutoring/choose_reserved_class_datetime/" + teacherId + "/");
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

