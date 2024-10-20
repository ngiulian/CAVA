goBtn.onclick = function() {
    var goBtn = document.getElementById("goBtn");
    var model = document.getElementById("dropdown_model").value;
    var topic = document.getElementById("dropdown_topic").value;
    if (model && topic) {
        window.location = model + "_" + topic + ".html";
    }
}

modeBtn.onclick = function() {
    window.location = "comparison.html";
}