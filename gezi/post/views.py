from django.shortcuts import render, HttpResponse
from .models import Sehir
from django.http import Http404

def homePageView(request):
    return render(request, 'firstPage.html')

def updateCityFiltered(value):
    sehirFiltered = value

def detail(request):
    #sehirler = Sehir.objects.all()
    query = request.GET['lastname']
    sehirler = Sehir.objects.filter(il__startswith=query)
    context = {
        'sehirler': sehirler,
    }
    #Html koduna ilgili değerleri context ile gönderiyoruz
    return render(request, 'detailPage.html', context)

def result(request, sehir_id):
    # return HttpResponse("<h2>Seçim sonucu sonuçlanmış ekranın gelmesi </h2>")
    try:
        sehir = Sehir.objects.get(pk=sehir_id)
        context = {
            'sehir': sehir,
        }
    except Sehir.DoesNotExist:
        raise Http404("Yetkiniz bulunmamaktadır...")
    return render(request, 'resultPage.html', context)
