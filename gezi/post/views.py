import pandas as pd
from django.shortcuts import render, HttpResponse
from .models import Sehir,AltSehir,Oteller,Restaurantlar
from django.http import Http404
from .TravelAlgorithm.src.travelAlgorithm import findRoute
from django_pandas.io import read_frame
from .Enums.EnumPackage import MODState,rotaStateEnum
from .Utilities.utilities import uzaklikHesaplama
import geocoder
from math import sqrt
from itertools import chain

choosenCitiesList = []
subCitiesList = []
subHotelList = []
subRestaurantList = []
rotaStateFlag = rotaStateEnum.firstState
firstPageRefresh = "Yes"
globalModState = MODState.ilSecimi
activateRotate = "No"
activateHotel = "No"
activeRestaurant = "No"

def homePageView(request):
    global rotaStateFlag
    global activateRotate
    global activateHotel
    global activeRestaurant
    global firstPageRefresh
    global choosenCitiesList

    activateRotate="No"
    activateHotel = "No"
    activeRestaurant = "No"
    firstPageRefresh = "Yes" #Ana ekrandan diğer ekrana geçerken otel ve restaurantların temizlenip temizlenmemesi olayı için

    rotaStateFlag = rotaStateEnum.firstState
    return render(request, 'firstPage.html')

def detail(request):

    global activateRotate
    global activateHotel
    global activeRestaurant
    global rotaStateFlag
    global globalModState
    global globalCheckList
    global globalQuery
    global firstPageRefresh
    global choosenCitiesList

    if rotaStateFlag == rotaStateEnum.firstState: # Bu rota belirlemede tekrar sayfanın yüklenmesi için gerekli State
            firstPageRefresh = "Yes"
            modState = MODState.ilSecimi
            checkList = request.GET.getlist('checks[]')
            globalCheckList = checkList
            query = request.GET['lastname']
            globalQuery = query

            if len(checkList) != 0:
                for j in range(len(checkList)):
                    if checkList[j]=="mod":
                        modState = MODState.yakinCevre


            if modState == MODState.yakinCevre:
                if query.isdigit():
                    rotaStateFlag = rotaStateEnum.secondState
                    globalModState = MODState.yakinCevre
                    value = int(query)
                    #Buraya mesafe arasinda şehirler listelenip eklenicek
                    context = findNearestPlaces(request, value)
                    return render(request, 'resultPage.html', context)
                else:
                    return render(request, "wrongValue.html")

            elif modState == MODState.ilSecimi:
                if query.isalpha():
                    rotaStateFlag = rotaStateEnum.secondState
                    globalModState = MODState.ilSecimi
                    #Secili sehir id sini gönderiyoruz
                    sehirID = Sehir.objects.filter(il=query).values('id')[0]['id']
                    context = cityResult(request, sehirID)
                    return render(request, 'resultPage.html', context)

                else:
                    return render(request, "wrongValue.html")
            else:
                return render(request, 'block.html')

    else:
        firstPageRefresh = "No"
        completed = request.GET.get('changeStatus1', '')


        try:
           if completed == "actionState":
               rotaStateFlag = rotaStateEnum.thirdState
           else:
               rotaStateFlag = rotaStateEnum.secondState
        except:
            print("ERRORR")

        updateActiveCity(request)

        if rotaStateFlag == rotaStateEnum.secondState:
            activateRotate = "No"
            if len(globalCheckList) != 0:
                for j in range(len(globalCheckList)):
                    if globalCheckList[j] == "mod":
                        globalModState = MODState.yakinCevre

            if globalModState == MODState.yakinCevre:
                if globalQuery.isdigit():
                    rotaStateFlag = rotaStateEnum.secondState
                    globalModState = MODState.yakinCevre
                    value = int(globalQuery)
                    # Buraya mesafe arasinda şehirler listelenip eklenicek
                    context = findNearestPlaces(request, value)
                    return render(request, 'resultPage.html', context)
                else:
                    return render(request, "wrongValue.html")

            elif globalModState == MODState.ilSecimi:
                if globalQuery.isalpha():
                    rotaStateFlag = rotaStateEnum.secondState
                    globalModState = MODState.ilSecimi
                    # Secili sehir id sini gönderiyoruz
                    sehirID = Sehir.objects.filter(il=globalQuery).values('id')[0]['id']
                    context = cityResult(request, sehirID)
                    return render(request, 'resultPage.html', context)

                else:
                    return render(request, "wrongValue.html")
            else:
                return render(request, 'block.html')


        elif rotaStateFlag == rotaStateEnum.thirdState:
            activateRotate = "Yes"
            #rotaStateFlag = True  # Bu rota belirlemede tekrar sayfanın yüklenmesi için gerekli State
            if globalModState == MODState.yakinCevre:
                # Buraya mesafe arasinda şehirler listelenip eklenicek
                context = findNearestPlacesMap(request)
                return render(request, 'resultPage.html', context)

            elif globalModState == MODState.ilSecimi:
                context = cityResultMap(request)
                return render(request, 'resultPage.html', context)

            else:
                 return render(request, 'block.html')


#Bulunan sehir için altSehirler listelenip en kısa mesafe bulunup ilgili ekran açılıyor
def cityResult(request,sehirID):
    try:
        altSehirler = AltSehir.objects.filter(sehir_id=sehirID)
        oteller = Oteller.objects.filter(sehir_id=sehirID)
        restaurantlar = Restaurantlar.objects.filter(sehir_id=sehirID)

        global activateRotate
        global activateHotel
        global activeRestaurant
        global subCitiesList
        global rotaStateFlag
        global subHotelList
        global subRestaurantList
        global firstPageRefresh
        global choosenCitiesList

        # -------------------    Verileri çekme denemeleri ----------------------
        altSehirlerFrame = read_frame(altSehirler)
        otellerFrame = read_frame(oteller)
        restaurantlarFrame = read_frame(restaurantlar)
        # ---- Sıralanmıs Sehirlerin İsimlerini çekiyoruz sıralı şekilde
        sortedCitiesNameList = []
        sortedCitiesLatList = []
        sortedCitiesLonList = []
        sortedCitiesSize = []

        subCitiesList = altSehirler
        subHotelList = oteller
        subRestaurantList = restaurantlar

        #----- Oteller Listesi
        hotelsNameList = []
        hotelsLatList = []
        hotelsLonList = []
        hotelsSize = []

        for a in range(0, len(subHotelList)):
            hotelsNameList.append(otellerFrame.iloc[a]['otelAdi'])
            hotelsLatList.append(otellerFrame.iloc[a]['konumX'])
            hotelsLonList.append(otellerFrame.iloc[a]['konumY'])
            hotelsSize.append(int(a))

        #----- Restaurantlar Listesi
        RestaurantsNameList = []
        RestaurantsLatList = []
        RestaurantsLonList = []
        RestaurantsSize = []

        for a in range(0, len(subRestaurantList)):
            RestaurantsNameList.append(restaurantlarFrame.iloc[a]['restaurantAdi'])
            RestaurantsLatList.append(restaurantlarFrame.iloc[a]['konumX'])
            RestaurantsLonList.append(restaurantlarFrame.iloc[a]['konumY'])
            RestaurantsSize.append(int(a))


        wayPointFlag = False
        context = {
            'altSehirler': subCitiesList,
            'sortedCitiesNameList': sortedCitiesNameList,
            'sortedCitiesLatList': sortedCitiesLatList,
            'sortedCitiesLonList': sortedCitiesLonList,
            'sortedCitiesSize': sortedCitiesSize,
            'hotelS': subHotelList,
            'hotelsNameList': hotelsNameList,
            'hotelsLatList': hotelsLatList,
            'hotelsLonList': hotelsLonList,
            'hotelsSize': hotelsSize,
            'restaurantS': subRestaurantList,
            'RestaurantsNameList': RestaurantsNameList,
            'RestaurantsLatList': RestaurantsLatList,
            'RestaurantsLonList': RestaurantsLonList,
            'RestaurantsSize': RestaurantsSize,
            'activateRotate': activateRotate,
            'activateHotel': activateHotel,
            'activeRestaurant': activeRestaurant,
            'rotaStateFlag': str(rotaStateEnum(rotaStateFlag).value),
            'firstPageRefresh': firstPageRefresh,
        }

    except Sehir.DoesNotExist:
        raise Http404("Yetkiniz bulunmamaktadır...")

    return context

def cityResultMap(request):
    try:
        # -------------------    Verileri çekme denemeleri ----------------------
        global activateRotate
        global subCitiesList
        global rotaStateFlag
        global subHotelList
        global subRestaurantList
        global firstPageRefresh
        global choosenCitiesList

        altSehirlerFrame = read_frame(choosenCitiesList)
        otellerFrame = read_frame(subHotelList)
        restaurantlarFrame = read_frame(subRestaurantList)
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

        #----- Oteller Listesi
        hotelsNameList = []
        hotelsLatList = []
        hotelsLonList = []
        hotelsSize = []

        for a in range(0, len(subHotelList)):
            hotelsNameList.append(otellerFrame.iloc[a]['otelAdi'])
            hotelsLatList.append(otellerFrame.iloc[a]['konumX'])
            hotelsLonList.append(otellerFrame.iloc[a]['konumY'])
            hotelsSize.append(int(a))

        #----- Restaurantlar Listesi
        RestaurantsNameList = []
        RestaurantsLatList = []
        RestaurantsLonList = []
        RestaurantsSize = []

        for a in range(0, len(subRestaurantList)):
            RestaurantsNameList.append(restaurantlarFrame.iloc[a]['restaurantAdi'])
            RestaurantsLatList.append(restaurantlarFrame.iloc[a]['konumX'])
            RestaurantsLonList.append(restaurantlarFrame.iloc[a]['konumY'])
            RestaurantsSize.append(int(a))

        wayPointFlag = True
        context = {
            'altSehirler': subCitiesList,
            'sortedCitiesNameList': sortedCitiesNameList,
            'sortedCitiesLatList': sortedCitiesLatList,
            'sortedCitiesLonList': sortedCitiesLonList,
            'sortedCitiesSize': sortedCitiesSize,
            'hotelS': subHotelList,
            'hotelsNameList': hotelsNameList,
            'hotelsLatList': hotelsLatList,
            'hotelsLonList': hotelsLonList,
            'hotelsSize': hotelsSize,
            'restaurantS': subRestaurantList,
            'RestaurantsNameList': RestaurantsNameList,
            'RestaurantsLatList': RestaurantsLatList,
            'RestaurantsLonList': RestaurantsLonList,
            'RestaurantsSize': RestaurantsSize,
            'activateRotate': activateRotate,
            'rotaStateFlag': str(rotaStateEnum(rotaStateFlag).value),
            'firstPageRefresh': firstPageRefresh,
        }

    except Sehir.DoesNotExist:
        raise Http404("Yetkiniz bulunmamaktadır...")

    return context

#--!!! Kişinin konumundan kaç km uzaklıktaki yerleri bulmasını istediğimizde çalışacak fonksiyon
def findNearestPlaces(request,length):
    try:
        global activateRotate
        global subCitiesList
        global rotaStateFlag
        global subHotelList
        global subRestaurantList
        global firstPageRefresh
        global choosenCitiesList

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
        # ---- Sıralanmıs Sehirlerin İsimlerini çekiyoruz sıralı şekilde
        subCitiesList = resultCitiesList

        #--- --------------------------OTELLER ---------------------------------------------------------
        allOteller = Oteller.objects.all()
        oteller = read_frame(allOteller)
        resultOtelList = []


        # --------OTEL Belirtilen uzunluktaki filtre yapıldıktan sonra hangi gezilecek yerlerin olduğunun listesi yapılıyor.
        for a in range(len(oteller)):
            #temp = sqrt(abs(mylocX - altSehirler.iloc[a]['konumX'])**2 + (abs(mylocY - altSehirler.iloc[a]['konumY']))**2)
            temp = uzaklikHesaplama(mylocX,mylocY,oteller.iloc[a]['konumX'],oteller.iloc[a]['konumY'])
            if temp <= length:
                resultOtelList.append(oteller.iloc[a])

        # ---- Sıralanmıs Sehirlerin İsimlerini çekiyoruz sıralı şekilde
        subHotelList = resultOtelList
        # ----- Oteller Listesi
        hotelsNameList = []
        hotelsLatList = []
        hotelsLonList = []
        hotelsSize = []

        for a in range(0, len(subHotelList)):
            hotelsNameList.append(oteller.iloc[a]['otelAdi'])
            hotelsLatList.append(oteller.iloc[a]['konumX'])
            hotelsLonList.append(oteller.iloc[a]['konumY'])
            hotelsSize.append(int(a))

        #----------------------------------------------------------------------------------------------------------------------------


        #--- --------------------------RESTAURANTLAR ---------------------------------------------------------
        allRestaurantlar = Restaurantlar.objects.all()
        restaurantlar = read_frame(allRestaurantlar)
        resultRestaurantList = []


        # --------RESTAURANTLAR Belirtilen uzunluktaki filtre yapıldıktan sonra hangi gezilecek yerlerin olduğunun listesi yapılıyor.
        for a in range(len(restaurantlar)):
            #temp = sqrt(abs(mylocX - altSehirler.iloc[a]['konumX'])**2 + (abs(mylocY - altSehirler.iloc[a]['konumY']))**2)
            temp = uzaklikHesaplama(mylocX,mylocY,restaurantlar.iloc[a]['konumX'],restaurantlar.iloc[a]['konumY'])
            if temp <= length:
                resultRestaurantList.append(restaurantlar.iloc[a])
        # ---- Sıralanmıs Sehirlerin İsimlerini çekiyoruz sıralı şekilde
        subRestaurantList = resultRestaurantList
        # ----- RESTAURANTLAR Listesi
        RestaurantsNameList = []
        RestaurantsLatList = []
        RestaurantsLonList = []
        RestaurantsSize = []

        for a in range(0, len(subRestaurantList)):
            RestaurantsNameList.append(restaurantlar.iloc[a]['restaurantAdi'])
            RestaurantsLatList.append(restaurantlar.iloc[a]['konumX'])
            RestaurantsLonList.append(restaurantlar.iloc[a]['konumY'])
            RestaurantsSize.append(int(a))

        #----------------------------------------------------------------------------------------------------------------------------


        sortedCitiesNameList = []
        sortedCitiesLatList = []
        sortedCitiesLonList = []
        sortedCitiesSize = []

        none_qs = AltSehir.objects.none()
        foundCities = list(chain(none_qs, resultCitiesList))

        wayPointFlag = False
        context = {
            'altSehirler': subCitiesList,
            'sortedCitiesNameList': sortedCitiesNameList,
            'sortedCitiesLatList': sortedCitiesLatList,
            'sortedCitiesLonList': sortedCitiesLonList,
            'sortedCitiesSize': sortedCitiesSize,
            'hotelS': subHotelList,
            'hotelsNameList': hotelsNameList,
            'hotelsLatList': hotelsLatList,
            'hotelsLonList': hotelsLonList,
            'hotelsSize': hotelsSize,
            'restaurantS': subRestaurantList,
            'RestaurantsNameList': RestaurantsNameList,
            'RestaurantsLatList': RestaurantsLatList,
            'RestaurantsLonList': RestaurantsLonList,
            'RestaurantsSize': RestaurantsSize,
            'activateRotate': activateRotate,
            'rotaStateFlag': str(rotaStateEnum(rotaStateFlag).value),
            'firstPageRefresh': firstPageRefresh,
        }

    except Sehir.DoesNotExist:
        raise Http404("Yetkiniz bulunmamaktadır...")

    return context

def findNearestPlacesMap(request):
    try:
        global activateRotate
        global subCitiesList
        global rotaStateFlag
        global subHotelList
        global subRestaurantList
        global firstPageRefresh
        global choosenCitiesList

        myloc = geocoder.ip('me')
        print("My Location =",myloc.latlng)
        mylocX = myloc.latlng[0]
        mylocY = myloc.latlng[1]

        resultCities = pd.DataFrame(choosenCitiesList)
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

            # --- --------------------------OTELLER ---------------------------------------------------------
            otellerFrame = pd.DataFrame(subHotelList)
            # ----- Oteller Listesi
            hotelsNameList = []
            hotelsLatList = []
            hotelsLonList = []
            hotelsSize = []

            for a in range(0, len(subHotelList)):
                hotelsNameList.append(otellerFrame.iloc[a]['otelAdi'])
                hotelsLatList.append(otellerFrame.iloc[a]['konumX'])
                hotelsLonList.append(otellerFrame.iloc[a]['konumY'])
                hotelsSize.append(int(a))

            # ----------------------------------------------------------------------------------------------------------------------------

            # --- --------------------------RESTAURANTLAR ---------------------------------------------------------
            restaurantlarFrame = pd.DataFrame(subRestaurantList)
            # ----- RESTAURANTLAR Listesi
            RestaurantsNameList = []
            RestaurantsLatList = []
            RestaurantsLonList = []
            RestaurantsSize = []

            for a in range(0, len(subRestaurantList)):
                RestaurantsNameList.append(restaurantlarFrame.iloc[a]['restaurantAdi'])
                RestaurantsLatList.append(restaurantlarFrame.iloc[a]['konumX'])
                RestaurantsLonList.append(restaurantlarFrame.iloc[a]['konumY'])
                RestaurantsSize.append(int(a))

            # ----------------------------------------------------------------------------------------------------------------------------


        none_qs = AltSehir.objects.none()
        foundCities = list(chain(none_qs, subCitiesList))

        wayPointFlag = True
        context = {
            'altSehirler': subCitiesList,
            'sortedCitiesNameList': sortedCitiesNameList,
            'sortedCitiesLatList': sortedCitiesLatList,
            'sortedCitiesLonList': sortedCitiesLonList,
            'sortedCitiesSize': sortedCitiesSize,
            'hotelS': subHotelList,
            'hotelsNameList': hotelsNameList,
            'hotelsLatList': hotelsLatList,
            'hotelsLonList': hotelsLonList,
            'hotelsSize': hotelsSize,
            'restaurantS': subRestaurantList,
            'RestaurantsNameList': RestaurantsNameList,
            'RestaurantsLatList': RestaurantsLatList,
            'RestaurantsLonList': RestaurantsLonList,
            'RestaurantsSize': RestaurantsSize,
            'activateRotate': activateRotate,
            'rotaStateFlag': str(rotaStateEnum(rotaStateFlag).value),
            'firstPageRefresh': firstPageRefresh,
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


def updateRotateStateFlagFunction(value):
    global rotaStateFlag
    if rotaStateFlag == rotaStateEnum.secondState:
        rotaStateFlag = rotaStateEnum.thirdState
    return rotaStateFlag

def updateActiveCity(request):
    global subCitiesList
    global choosenCitiesList
    lastCities =[]
    activecities = request.GET.getlist('cityChecks[]')
    print("Tip = ",subCitiesList[0]['yerAdi'])
    print("CitieA =",subCitiesList)

    for i in range(len(activecities)):
        for j in range(len(subCitiesList)):
            if activecities[i] == subCitiesList[j]['yerAdi']:
                lastCities.append(subCitiesList[j])

    if len(lastCities) != 0:
        choosenCitiesList = lastCities