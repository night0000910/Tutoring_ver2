$(document).ready(function() {
    $('.collapsible').collapsible();

    displayTeachersClass();
    createElementsForReservation();
})

/* これから行う予定の、1週間分の授業を表示する */
function displayTeachersClass(){
    var request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/api/v1/users/authenticated_teacher/classes/daily_classes/reserved_classes/");
    request.onload = createElementsOfTeachersClass;
    request.send()
}

function createElementsOfTeachersClass(){
    var response = JSON.parse(this.response);
    console.log(response);

    var ul = document.getElementById("teachers-class-container");

    if (response.length != 0){

        reservedClassArray = sortClassArray(response);

        for (var reservedClass of response){
            var li = document.createElement("li");
            li.setAttribute("class", "collection-item avatar");
            var a = document.createElement("a");
            a.setAttribute("href", "#");

            createImg(a);

            
        }


    } else{
        ul.remove()

    }
}

function sortClassArray(classArray){
    classArray.sort(function (x, y){
        x = new Date(x.year, x.month, x.day, x.hour);
        y = new Date(y.year, y.month, y.day, y.hour);

        return x.getTime() - y.getTime()
    });

}

function createImg(a){
    var img = document.createElement("img");

    var userId = 
    var request = new XMLHttpRequest();
    request.open("GET", );
}

/* 授業を予約するための要素を生成する */
function createElementsForReservation(){
    for (let i = 1; i <= 7; i++){
        var collapsibleHeader = document.getElementById("collapsible-header-" + i);
        var date = new Date();
        date.setDate(date.getDate() + i-1);
        collapsibleHeader.innerHTML += (date.getMonth() + 1) + "月" + date.getDate() + "日";

        var collapsibleBody = document.getElementById("collapsible-body-" + i);
        var collection = collapsibleBody.childNodes[1];
        date.setHours(0);
        date.setMinutes(0);
        date.setSeconds(0);
        for (let i = 0; i < 24; i++){
            var time = document.createElement("a");
            time.setAttribute("class", "collection-item");
            time.setAttribute("id", date.getFullYear() + "-" + (date.getMonth()+1) + "-" + date.getDate() + "-" + date.getHours())
            time.setAttribute("href", "http://127.0.0.1:8000/tutoring/add_teachers_class/" + date.getFullYear() + "/" + (date.getMonth()+1) + "/" + date.getDate() + "/" + date.getHours() + "/");
            time.innerHTML = date.getHours() + ":00";
            collection.appendChild(time);
            date.setHours(date.getHours() + 1);
        }
    }

    var userId = Number(document.getElementById("user-id").getAttribute("value"));

    var request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/api/v1/users/" + userId + "/classes/weekly_classes/");
    request.onload = distinguishTeachersClass;
    request.send();
}

function distinguishTeachersClass(){
    var response = JSON.parse(this.response);

    for (var datetime of response){
        var datetime = new Date(datetime.year, (datetime.month-1), datetime.day, (datetime.hour+9)); /* UTCをJSTに変換 */

        var id = datetime.getFullYear() + "-" + (datetime.getMonth()+1) + "-" + datetime.getDate() + "-" + datetime.getHours();
        console.log(id);

        if (document.getElementById(id) != null){
            var time = document.getElementById(id);
            time.setAttribute("href", "#");
            time.innerHTML += '<span class="badge">reserved</span>';
        }
    }
}