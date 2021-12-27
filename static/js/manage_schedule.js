$(document).ready(function() {
    $('.collapsible').collapsible();

    for (let i = 1; i <= 7; i++){
        collapsibleHeader = document.getElementById("collapsible-header-" + i);
        date = new Date();
        date.setDate(date.getDate() + i-1);
        collapsibleHeader.innerHTML += (date.getMonth() + 1) + "月" + date.getDate() + "日";

        collapsibleBody = document.getElementById("collapsible-body-" + i);
        collection = collapsibleBody.childNodes[1];
        date.setHours(0);
        date.setMinutes(0);
        date.setSeconds(0);
        for (let i = 0; i < 24; i++){
            time = document.createElement("a");
            time.setAttribute("class", "collection-item");
            time.setAttribute("id", date.getFullYear() + "-" + (date.getMonth()+1) + "-" + date.getDate() + "-" + date.getHours())
            time.setAttribute("href", "http://127.0.0.1:8000/tutoring/add_teachers_class/" + date.getFullYear() + "/" + (date.getMonth()+1) + "/" + date.getDate() + "/" + date.getHours() + "/");
            time.innerHTML = date.getHours() + ":00";
            collection.appendChild(time);
            date.setHours(date.getHours() + 1);
        }
    }

    request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/api/v1/");
})

