import pandas
from django.shortcuts import render, HttpResponse
from .models import Sehir,AltSehir
from django.http import Http404
from .TravelAlgorithm.src.travelAlgorithm import findRoute
from django_pandas.io import read_frame

def homePageView(request):
    return render(request, 'firstPage.html')

def detail(request):
    #sehirler = Sehir.objects.all()
    query = request.GET['lastname']
    sehirler = Sehir.objects.filter(il__startswith=query)
    context = {
        'sehirler': sehirler,
    }
    #Html koduna ilgili değerleri context ile gönderiyoruz
    return render(request, 'detailPage.html', context)

def result(request, sehirAdi, sehirID):
    try:
        altSehirler = AltSehir.objects.filter(sehir_id=sehirID)

        # -------------------    Verileri çekme denemeleri ----------------------
        altSehirlerFrame = read_frame(altSehirler)

        for col in altSehirlerFrame.columns:
            print(col)

        print("altSehir Tipi=",altSehirlerFrame.iloc[0]['konumX'])
        print("altSehir Tipi=", altSehirlerFrame.iloc[0]['yerAdi'])

        # ------------------------------------------------------------------------

        context = {
            'altSehirler': altSehirler,
        }

        findRoute()

    except Sehir.DoesNotExist:
        raise Http404("Yetkiniz bulunmamaktadır...")
    return render(request, 'resultPage.html', context)
