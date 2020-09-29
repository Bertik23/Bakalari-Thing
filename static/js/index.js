function loadNewTimetable(){
    fetch('/loadNewTimetable?date='+document.getElementById("timetableDate").value)
        .then((response) => {
            return response.json();
        })
        .then((myJson) => {
            //console.log(document.getElementById("timetable").innerHTML == myJson.result);
            document.getElementById("timetable").innerHTML = myJson.result;
        });
}

function getBaseUrl(){
    var getUrl = window.location;
    return getUrl .protocol + "//" + getUrl.host + "/" + getUrl.pathname.split('/')[1];
}

function redirect(url){
    location.replace(getBaseUrl()+url);
}

function login(){
    fetch("/login?username=" + document.getElementById("username").value + "&password=" + document.getElementById("password").value)
        .then((res) => {
            return res.json();
        })
        .then((myJson) => {
            console.log(myJson)
            if (myJson.response == "success"){
                redirect("timetable")
            }
            else if (myJson.response == "error"){
                if (myJson.type == "WrongLogin"){
                    document.getElementById("WrongLogin").style = "display: block;"
                }
                else if (myJson.type == "NoConnection"){
                    var errorDiv = document.getElementById("error")
                    errorDiv.style = "display: block;"
                    errorDiv.innerHTML = myJson.message;
                }
            }
        })
}

Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});

function loadMarks(){
    fetch("/getMarks")
        .then((response) =>{
            return response.json()
        })
        .then((myJson) => {
            document.getElementById("marks").innerHTML = myJson.result;
        })
}

function getRecievedMessages(){
    fetch("/getRecievedMessages")
        .then((response) => {
            return response.json()
        })
        .then((myJson) => {
            document.getElementById("messages").innerHTML = myJson.result;
        })
}