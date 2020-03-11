import pandas as pd
from django.shortcuts import render, HttpResponse
from .models import Sehir,AltSehir
from django.http import Http404
from .TravelAlgorithm.src.travelAlgorithm import findRoute
from django_pandas.io import read_frame
from .Enums.EnumPackage import MODState
from .Utilities.utilities import uzaklikHesaplama

import geocoder
from math import sqrt
from itertools import chain

def homePageView(request):
    return render(request, 'firstPage.html')

def detail(request):
    modState = MODState.ilSecimi
    checkList = request.GET.getlist('checks[]')
    query = request.GET['lastname']

    if len(checkList) != 0:
        for j in range(len(checkList)):
            if checkList[j]=="mod":
                modState = MODState.yakinCevre


    if modState == MODState.yakinCevre:
        if query.isdigit():
            value = int(query)
            #Buraya mesafe arasinda şehirler listelenip eklenicek
            context = findNearestPlaces(request, value)
            return render(request, 'resultPage.html', context)
        else:
            return render(request, "wrongValue.html")

    elif modState == MODState.ilSecimi:
        if query.isalpha():
            #Secili sehir id sini gönderiyoruz
            sehirID = Sehir.objects.filter(il=query).values('id')[0]['id']
            context = cityResult(request, sehirID)
            return render(request, 'resultPage.html', context)

        else:
            return render(request, "wrongValue.html")
    else:
        return render(request, 'block.html')


#Bulunan sehir için altSehirler listelenip en kısa mesafe bulunup ilgili ekran açılıyor
def cityResult(request,sehirID):
    try:
        altSehirler = AltSehir.objects.filter(sehir_id=sehirID)

        # -------------------    Verileri çekme denemeleri ----------------------
        altSehirlerFrame = read_frame(altSehirler)

        for col in range(len(altSehirlerFrame)):
            print("Sehir=",altSehirlerFrame.iloc[col]['yerAdi'])
        #-------------------- Database'deki verileri uygun formata çeviriyoruz ----------
        writeTSPFile(altSehirlerFrame)
        # -------------------------- Sıralanmıs Sehir Listesini alıyoruz----------------------------------------------
        sortedCities = findRoute()

        #---- Sıralanmıs Sehirlerin İsimlerini çekiyoruz sıralı şekilde
        sortedCitiesNameList = []
        sortedCitiesLatList = []
        sortedCitiesLonList= []
        sortedCitiesSize = []

        for a in range(1, len(sortedCities)):
            sortedCitiesNameList.append(altSehirlerFrame.iloc[int(sortedCities.iloc[a]['city'])-2]['yerAdi'])
            sortedCitiesLatList.append(altSehirlerFrame.iloc[int(sortedCities.iloc[a]['city'])-2]['konumX'])
            sortedCitiesLonList.append(altSehirlerFrame.iloc[int(sortedCities.iloc[a]['city']) - 2]['konumY'])
            sortedCitiesSize.append(int(a))
            print("TEST=",altSehirlerFrame.iloc[int(sortedCities.iloc[a]['city'])-2]['yerAdi'])

        context = {
            'altSehirler': altSehirler,
            'sortedCitiesNameList': sortedCitiesNameList,
            'sortedCitiesLatList': sortedCitiesLatList,
            'sortedCitiesLonList': sortedCitiesLonList,
            'sortedCitiesSize': sortedCitiesSize,
        }

    except Sehir.DoesNotExist:
        raise Http404("Yetkiniz bulunmamaktadır...")

    return context

def writeTSPFile(altSehirlerFrame):
    dosya = open("sehirBilgileri.tsp", "w")

    dosya.write("""NAME : ar9152
COMMENT : 9152 locations in Argentina
COMMENT : Derived from National Imagery and Mapping Agency data
TYPE : TSP\n""")
    dimension = "DIMENSION : "+str(len(altSehirlerFrame)+1)
    dosya.write(dimension)
    dosya.write("""
EDGE_WEIGHT_TYPE : EUC_2D
NODE_COORD_SECTION
""")

    myloc = geocoder.ip('me')
    mylocList = myloc.latlng
    mylocValue = "1"+" "+str(mylocList[0])+" "+str(mylocList[1])+"\n"
    dosya.write(mylocValue)

    for col in range(len(altSehirlerFrame)):
        value = str(col+2) + " " + str(altSehirlerFrame.iloc[col]['konumX'])+" "+str(altSehirlerFrame.iloc[col]['konumY'])+"\n"
        dosya.write(value)

    dosya.write("EOF")
    dosya.close()

#--!!! Kişinin konumundan kaç km uzaklıktaki yerleri bulmasını istediğimizde çalışacak fonksiyon
def findNearestPlaces(request,length):
    try:
        myloc = geocoder.ip('me')
        print("My Location =",myloc.latlng)
        mylocX = myloc.latlng[0]
        mylocY = myloc.latlng[1]

        allAltSehirler = AltSehir.objects.all()
        altSehirler = read_frame(allAltSehirler)

        resultCitiesList = []


        # -------- Belirtilen uzunluktaki filtre yapıldıktan sonra hangi gezilecek yerlerin olduğunun listesi yapılıyor.
        for a in range(len(altSehirler)):
            #temp = sqrt(abs(mylocX - altSehirler.iloc[a]['konumX'])**2 + (abs(mylocY - altSehirler.iloc[a]['konumY']))**2)
            temp = uzaklikHesaplama(mylocX,mylocY,altSehirler.iloc[a]['konumX'],altSehirler.iloc[a]['konumY'])
            if temp <= length:
                resultCitiesList.append(altSehirler.iloc[a])

        resultCities = pd.DataFrame(resultCitiesList)
        writeTSPFile(resultCities)

        # -------------------------- Sıralanmıs Sehir Listesini alıyoruz----------------------------------------------
        sortedCities = findRoute()

        # ---- Sıralanmıs Sehirlerin İsimlerini çekiyoruz sıralı şekilde
        sortedCitiesNameList = []
        sortedCitiesLatList = []
        sortedCitiesLonList = []
        sortedCitiesSize = []
        for a in range(1, len(sortedCities)):
            sortedCitiesNameList.append(resultCities.iloc[int(sortedCities.iloc[a]['city']) - 2]['yerAdi'])
            sortedCitiesLatList.append(resultCities.iloc[int(sortedCities.iloc[a]['city']) - 2]['konumX'])
            sortedCitiesLonList.append(resultCities.iloc[int(sortedCities.iloc[a]['city']) - 2]['konumY'])
            sortedCitiesSize.append(int(a)-1)

        none_qs = AltSehir.objects.none()
        foundCities = list(chain(none_qs, resultCitiesList))

        context = {
            'altSehirler': foundCities,
            'sortedCitiesNameList': sortedCitiesNameList,
            'sortedCitiesLatList': sortedCitiesLatList,
            'sortedCitiesLonList': sortedCitiesLonList,
            'sortedCitiesSize': sortedCitiesSize,
        }

    except Sehir.DoesNotExist:
        raise Http404("Yetkiniz bulunmamaktadır...")

    return context