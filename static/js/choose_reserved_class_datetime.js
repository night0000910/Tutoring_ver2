$(document).ready(function() {
    $('.collapsible').collapsible();

    userId = Number(document.getElementById("user-id").getAttribute("value"));
    teacherId = Number(document.getElementById("teacher-id").getAttribute("value"));

    request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/api/v1/users/" + teacherId + "/classes/weekly_classes/");
    request.onload = displayTeachersClass;
    request.send();
})

function displayTeachersClass(){
    response = JSON.parse(this.response);
    datetimeArray = createDatetimeArray(response);
    dateArray = createDateArray(datetimeArray);

    createElements(dateArray, datetimeArray);
}

function createDatetimeArray(response){
    datetimeArray = response

    for (var i = 0; i <= datetimeArray.length-1; i++){
        datetime = datetimeArray[i];
        datetime = new Date(datetime.year, datetime.month-1, datetime.day, datetime.hour+9);
        datetimeArray[i] = {year : datetime.getFullYear(), month : datetime.getMonth()+1, day : datetime.getDate(), hour : datetime.getHours()};
    }

    datetimeArray.sort(function (x, y){
        x = new Date(x.year, x.month, x.day, x.hour);
        y = new Date(y.year, y.month, y.day, y.hour);

        return x.getTime() - y.getTime()
    });

    return datetimeArray
}

/* datetimeArrayには、日付時刻が早い順に並べ替えられたDateオブジェクトのArrayオブジェクトを渡す必要がある */
function createDateArray(datetimeArray){
    dateArray = new Array(datetimeArray[0]);

    for (var i = 1; i <= (datetimeArray.length-1); i++){

        x = datetimeArray[i];
        y = datetimeArray[i-1];

        if (!(x.year == y.year && x.month == y.month && x.day == y.day)){
            dateArray.push(datetimeArray[i]);
        }
    }

    return dateArray;
}

function createElements(dateArray, datetimeArray){

    for (var date of dateArray){

        li = document.createElement("li");
        collapsibleHeader = document.createElement("div");
        collapsibleHeader.setAttribute("class", "collapsible-header");
        collapsibleHeader.innerHTML = '<i class="material-icons">create</i>' + date.month + "月" + date.day + "日" + "</div>"
        collapsibleBody = document.createElement("div");
        collapsibleBody.setAttribute("class", "collapsible-body");
        collection = document.createElement("div");
        collection.setAttribute("class", "collection");
        collection.setAttribute("id", date.year + "-" + date.month + "-" + date.day);

        li.appendChild(collapsibleHeader);
        li.appendChild(collapsibleBody);
        collapsibleBody.appendChild(collection);

        ul = document.getElementById("ul");
        ul.appendChild(li);
    }

    for (var datetime of datetimeArray){
        a = document.createElement("a");
        a.setAttribute("class", "collection-item");
        a.setAttribute("href", "#");
        a.innerHTML = datetime.hour + ":00";

        div = document.getElementById(datetime.year + "-" + datetime.month + "-" + datetime.day);
        div.appendChild(a);
    }
}