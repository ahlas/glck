import pandas
from django.shortcuts import render, HttpResponse
from .models import Sehir,AltSehir
from django.http import Http404
from .TravelAlgorithm.src.travelAlgorithm import findRoute
from django_pandas.io import read_frame
from .Enums.EnumPackage import MODState

import geocoder
from math import sqrt

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
        else:
            return render(request, "wrongValue.html")

    elif modState == MODState.ilSecimi:
        if query.isalpha():
            sehirler = Sehir.objects.filter(il__startswith=query)
            context = {
                'sehirler': sehirler,
            }
            # Html koduna ilgili değerleri context ile gönderiyoruz
            return render(request, 'detailPage.html', context)
        else:
            return render(request, "wrongValue.html")
    else:
        return render(request, 'block.html')

    #sehirler = Sehir.objects.all()


def result(request, sehirAdi, sehirID):
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
        for a in range(len(sortedCities)):
            sortedCitiesNameList.append(altSehirlerFrame.iloc[int(sortedCities.iloc[a]['city'])-1]['yerAdi'])
            sortedCitiesLatList.append(altSehirlerFrame.iloc[int(sortedCities.iloc[a]['city'])-1]['konumX'])
            sortedCitiesLonList.append(altSehirlerFrame.iloc[int(sortedCities.iloc[a]['city']) - 1]['konumY'])
            sortedCitiesSize.append(int(a))
            print("TEST=",altSehirlerFrame.iloc[int(sortedCities.iloc[a]['city'])-1]['yerAdi'])

        context = {
            'altSehirler': altSehirler,
            'sortedCitiesNameList': sortedCitiesNameList,
            'sortedCitiesLatList': sortedCitiesLatList,
            'sortedCitiesLonList': sortedCitiesLonList,
            'sortedCitiesSize': sortedCitiesSize,
        }

    except Sehir.DoesNotExist:
        raise Http404("Yetkiniz bulunmamaktadır...")
    return render(request, 'resultPage.html', context)

def writeTSPFile(altSehirlerFrame):
    dosya = open("sehirBilgileri.tsp", "w")

    dosya.write("""NAME : ar9152
COMMENT : 9152 locations in Argentina
COMMENT : Derived from National Imagery and Mapping Agency data
TYPE : TSP\n""")
    dimension = "DIMENSION : "+str(len(altSehirlerFrame))
    dosya.write(dimension)
    dosya.write("""
EDGE_WEIGHT_TYPE : EUC_2D
NODE_COORD_SECTION
""")

    for col in range(len(altSehirlerFrame)):
        value = str(col+1) + " " + str(altSehirlerFrame.iloc[col]['konumX'])+" "+str(altSehirlerFrame.iloc[col]['konumY'])+"\n"
        dosya.write(value)

    dosya.write("EOF")
    dosya.close()

#--!!! Kişinin konumundan kaç km uzaklıktaki yerleri bulmasını istediğimizde çalışacak fonksiyon
def findNearestPlaces(request,length):

    myloc = geocoder.ip('me')
    print("My Location =",myloc.latlng)
    mylocX = myloc.latlng[0]
    mylocY = myloc.latlng[1]

    altSehirler = AltSehir.objects.all()
    resultCities = []

    # -------- Belirtilen uzunluktaki filtre yapıldıktan sonra hangi gezilecek yerlerin olduğunun listesi yapılıyor.
    for a in range(len(altSehirler)):
        temp = sqrt(abs(mylocX - altSehirler.iloc[a]['konumX'])**2 + (abs(mylocY - altSehirler.iloc[a]['konumY']))**2)
        if temp <= length:
            resultCities.append(altSehirler.iloc[a])
