function handleClick(cb) {
            if (cb.checked) {
                document.getElementById("searchArea").placeholder = "Km Giriniz...";
                document.getElementById("searchArea").value="";
            } else {
                document.getElementById("searchArea").placeholder = "Şehir İsmini Giriniz...";
                document.getElementById("searchArea").value="";
            }
}

function dynamicButton(url){
    document.getElementById("wayButton").style.visibility = "visible";
    window.location.href = url;
}