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
function dynamicButton(url){
    window.location.href = url;
}

// ROta bulma işlemi yaptırıldıktan sonra sayfanın wayPointleri göstermesi(rota çizgisini) için çalışan fonksiyon
function pageLoadFinishFunction(){
    document.getElementById("wayButton").click();
}