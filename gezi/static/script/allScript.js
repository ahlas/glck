function handleClick(cb) {
            if (cb.checked) {
                document.getElementById("searchArea").placeholder = "Km Giriniz...";
                document.getElementById("searchArea").value="";
            } else {
                document.getElementById("searchArea").placeholder = "Şehir İsmini Giriniz...";
                document.getElementById("searchArea").value="";
            }
}

// Sayfanın en kısa yolu bulduktan sonra tekrar update etmesi olayı için sayfa yenileme işlemi yaptırılıyor
function dynamicButton(url,checkboxList){
    //window.location.href = url;
    //window.location.reload(true);
    var checkedBoxes = getCheckedBoxes("cityChecks[]");
    if(checkedBoxes.length!=99999){
        localStorage.setItem("size",checkedBoxes.length.toString());
        for(var i=0; i<checkedBoxes.length;i++){
            var val = i.toString();
            localStorage.setItem(val, checkedBoxes[i]);
        }
        document.getElementById("xdemR").value="actionState";
        document.getElementById("xdemR1").click();
        return 1;
    }
    else{
        localStorage.setItem("size","-1");
        return 5;
    }

    //document.getElementById("xdemR").value = "True";

}

// ROta bulma işlemi yaptırıldıktan sonra sayfanın wayPointleri göstermesi(rota çizgisini) için çalışan fonksiyon
function pageLoadFinishFunction(){
    var value = document.getElementById("xdemR")
    document.getElementById("wayButton").click();
}



function getCheckedBoxes(chkboxName) {
  var checkboxes = document.getElementsByName(chkboxName);
  var checkboxesChecked = [];
  var unchecked = new Array(99999);
  // loop over them all
  for (var i=0; i<checkboxes.length; i++) {
     // And stick the checked ones onto an array...
     if (checkboxes[i].checked) {
        checkboxesChecked.push(checkboxes[i].value);
     }
  }
  // Return the array if it is non-empty, or null
  return checkboxesChecked.length > 0 ? checkboxesChecked : unchecked;
}

// Call as
