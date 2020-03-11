import math

def rad2deg(rad):
    return float(rad/math.pi*180.0)

def deg2Rad(deg):
    return float(deg*math.pi/180.0)

def uzaklikHesaplama(latitude1,longitude1,latitude2,longitude2):
    teta_degeri = longitude1 -longitude2
    mil = math.sin(deg2Rad(latitude1)) * math.sin(deg2Rad(latitude2)) + math.cos(deg2Rad(latitude1))* math.cos(deg2Rad(latitude2)) * math.cos(deg2Rad(teta_degeri))

    mil = math.acos(mil)
    mil = rad2deg(mil)
    mil = mil * 60 * 1.1515

    km = mil * 1.609344

    return km