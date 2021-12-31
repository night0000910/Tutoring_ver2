$(document).ready(function() {
    $('.collapsible').collapsible();

    var userId = Number(document.getElementById("user-id").getAttribute("value"));
    var teacherId = Number(document.getElementById("teacher-id").getAttribute("value"));

    var request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/api/v1/classes/weekly_classes/?teacher_id=" + teacherId + "&student_id=1");
    request.onload = displayTeachersClass;
    request.send();
})

function displayTeachersClass(){
    var response = JSON.parse(this.response);
    datetimeArray = createDatetimeArray(response); /* datetimeArrayはグローバル変数。displayReservedClassメソッドでも利用される。 */
    var dateArray = createDateArray(datetimeArray);

    createElements(dateArray, datetimeArray);

    var teacherId = Number(document.getElementById("teacher-id").getAttribute("value"));
    var userId = Number(document.getElementById("user-id").getAttribute("value"));
    var request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/api/v1/classes/weekly_classes/?teacher_id=" + teacherId + "&student_id=" + userId);
    request.onload = displayReservedClass;
    request.send();
}

function createDatetimeArray(response){
    var datetimeArray = response

    for (var i = 0; i <= datetimeArray.length-1; i++){
        var datetime = datetimeArray[i];
        datetime = new Date(datetime.year, datetime.month-1, datetime.day, datetime.hour+9); /* UTCをJSTに変換 */
        datetimeArray[i] = {year : datetime.getFullYear(), month : datetime.getMonth()+1, day : datetime.getDate(), hour : datetime.getHours()};
    }

    sortDatetimeArray(datetimeArray);

    return datetimeArray
}

function sortDatetimeArray(datetimeArray){
    datetimeArray.sort(function (x, y){
        x = new Date(x.year, x.month, x.day, x.hour);
        y = new Date(y.year, y.month, y.day, y.hour);

        return x.getTime() - y.getTime()
    });

}

/* datetimeArrayには、日付時刻が早い順に並べ替えられたDateオブジェクトのArrayオブジェクトを渡す必要がある */
function createDateArray(datetimeArray){
    var dateArray = new Array(datetimeArray[0]);

    for (var i = 1; i <= (datetimeArray.length-1); i++){

        var x = datetimeArray[i];
        var y = datetimeArray[i-1];

        if (!(x.year == y.year && x.month == y.month && x.day == y.day)){
            dateArray.push(datetimeArray[i]);
        }
    }

    return dateArray;
}

function createElements(dateArray, datetimeArray){

    for (var date of dateArray){

        var li = document.createElement("li");
        var collapsibleHeader = document.createElement("div");
        collapsibleHeader.setAttribute("class", "collapsible-header");
        collapsibleHeader.innerHTML = '<i class="material-icons">create</i>' + date.month + "月" + date.day + "日"
        var collapsibleBody = document.createElement("div");
        collapsibleBody.setAttribute("class", "collapsible-body");
        var collection = document.createElement("div");
        collection.setAttribute("class", "collection");
        collection.setAttribute("id", date.year + "-" + date.month + "-" + date.day);

        li.appendChild(collapsibleHeader);
        li.appendChild(collapsibleBody);
        collapsibleBody.appendChild(collection);

        var ul = document.getElementById("ul");
        ul.appendChild(li);
    }

    var teacherId = document.getElementById("teacher-id").getAttribute("value");

    for (var datetime of datetimeArray){
        var a = document.createElement("a");
        a.setAttribute("class", "collection-item");
        a.setAttribute("id", datetime.year + "-" + datetime.month + "-" + datetime.day + "-" + datetime.hour);
        a.setAttribute("href", "http://127.0.0.1:8000/tutoring/add_reserved_class/" + teacherId + "/" + datetime.year + "/" + datetime.month + "/" + datetime.day + "/" + datetime.hour + "/");
        a.innerHTML = datetime.hour + ":00";

        var div = document.getElementById(datetime.year + "-" + datetime.month + "-" + datetime.day);
        div.appendChild(a);
    }
}

function displayReservedClass(){
    var response = JSON.parse(this.response);

    for (var datetime of response){
        var datetime = new Date(datetime.year, (datetime.month-1), datetime.day, (datetime.hour+9)); /* UTCをJSTに変換 */
        datetime = {year : datetime.getFullYear(), month : datetime.getMonth()+1, day : datetime.getDate(), hour : datetime.getHours()};
        datetimeArray.push(datetime);
    }
    
    sortDatetimeArray(datetimeArray);

    addElements(datetimeArray);
}

function addElements(datetimeArray){
    var datetime = datetimeArray[0];
    var div = document.getElementById(datetime.year + "-" + datetime.month + "-" + datetime.day);
    var a = document.getElementById(datetime.year + "-" + datetime.month + "-" + datetime.day + "-" + datetime.hour);

    if (div == null){
        var li = document.createElement("li");
        var collapsibleHeader = document.createElement("div");
        collapsibleHeader.setAttribute("class", "collapsible-header");
        collapsibleHeader.innerHTML = '<i class="material-icons">create</i>' + datetime.month + "月" + datetime.day + "日"
        var collapsibleBody = document.createElement("div");
        collapsibleBody.setAttribute("class", "collapsible-body");
        var collection = document.createElement("div");
        collection.setAttribute("class", "collection");
        collection.setAttribute("id", datetime.year + "-" + datetime.month + "-" + datetime.day);

        li.appendChild(collapsibleHeader);
        li.appendChild(collapsibleBody);
        collapsibleBody.appendChild(collection);

        var ul = document.getElementById("ul");
        ul.insertBefore(li, ul.firstChild);

        var a = document.createElement("a");
        a.setAttribute("class", "collection-item");
        a.setAttribute("id", datetime.year + "-" + datetime.month + "-" + datetime.day + "-" + datetime.hour);
        a.setAttribute("href", "#");
        a.innerHTML = datetime.hour + ":00";
        a.innerHTML += '<span class="badge">reserved</span>';
        collection.insertBefore(a, collection.firstChild);

    } else if (a == null){
        var a = document.createElement("a");
        a.setAttribute("class", "collection-item");
        a.setAttribute("id", datetime.year + "-" + datetime.month + "-" + datetime.day + "-" + datetime.hour);
        a.setAttribute("href", "#");
        a.innerHTML = datetime.hour + ":00";
        a.innerHTML += '<span class="badge">reserved</span>';

        div.insertBefore(a, div.firstChild);
    }

    
    for (var i = 1; i <= datetimeArray.length-1; i++){
        var datetime = datetimeArray[i];
        var previousDatetime = datetimeArray[i-1];
        var div = document.getElementById(datetime.year + "-" + datetime.month + "-" + datetime.day);
        var a = document.getElementById(datetime.year + "-" + datetime.month + "-" + datetime.day + "-" + datetime.hour);

        if (div == null){
            var li = document.createElement("li");
            var collapsibleHeader = document.createElement("div");
            collapsibleHeader.setAttribute("class", "collapsible-header");
            collapsibleHeader.innerHTML = '<i class="material-icons">create</i>' + datetime.month + "月" + datetime.day + "日"
            var collapsibleBody = document.createElement("div");
            collapsibleBody.setAttribute("class", "collapsible-body");
            var collection = document.createElement("div");
            collection.setAttribute("class", "collection");
            collection.setAttribute("id", datetime.year + "-" + datetime.month + "-" + datetime.day);
    
            li.appendChild(collapsibleHeader);
            li.appendChild(collapsibleBody);
            collapsibleBody.appendChild(collection);

            var previousLi = document.getElementById(previousDatetime.year + "-" + previousDatetime.month + "-" + previousDatetime.day).parentElement.parentElement;
            var formerLi = previousLi.nextSibling;
            var ul = document.getElementById("ul");
            ul.insertBefore(li, formerLi);
    
            var a = document.createElement("a");
            a.setAttribute("class", "collection-item");
            a.setAttribute("id", datetime.year + "-" + datetime.month + "-" + datetime.day + "-" + datetime.hour);
            a.setAttribute("href", "#");
            a.innerHTML = datetime.hour + ":00";
            a.innerHTML += '<span class="badge">reserved</span>';
            collection.insertBefore(a, collection.firstChild);

        } else if (a == null){
            var a = document.createElement("a");
            a.setAttribute("class", "collection-item");
            a.setAttribute("id", datetime.year + "-" + datetime.month + "-" + datetime.day + "-" + datetime.hour);
            a.setAttribute("href", "#");
            a.innerHTML = datetime.hour + ":00";
            a.innerHTML += '<span class="badge">reserved</span>';

            var previousA = document.getElementById(previousDatetime.year + "-" + previousDatetime.month + "-" + previousDatetime.day + "-" + previousDatetime.hour);
            var divChildren = div.childNodes;
            var duplicate = false;

            for (var divChild of divChildren){

                if (divChild == previousA){
                    duplicate = true;
                }
            }
            
            if (duplicate == true){
                var formerA = previousA.nextSibling;
                div.insertBefore(a, formerA);

            } else{
                div.insertBefore(a, div.firstChild);
            }

        }

    }
}