from django.db import models

# Burada database kısmında oluşturmak istediğimiz model şekillerini oluşturmuş oluyoruz


class Sehir(models.Model):
    il = models.CharField(max_length=100)
    ilce = models.CharField(max_length=100)
    ilResim = models.CharField(max_length=1000)

    #Sehir modeli ile ilgili bilgi bakacağımızda hangi bilgi şeklinde gösterileceği (String olarak gösterim )
    def __str__(self):
        return self.il

class AltSehir(models.Model):
    sehir = models.ForeignKey(Sehir, on_delete=models.CASCADE)
    yerAdi = models.CharField(max_length=100)
    geziTür = models.CharField(max_length=100)
    konumX = models.FloatField()
    konumY = models.FloatField()

    def __str__(self):
        return self.yerAdi

class Oteller(models.Model):
    sehir       = models.ForeignKey(Sehir,on_delete=models.CASCADE)
    otelAdi     = models.CharField(max_length=100)
    otelYildiz  = models.CharField(max_length=10)
    konumX = models.FloatField()
    konumY = models.FloatField()

    def __str__(self):
        return self.otelAdi

class Restaurantlar(models.Model):
    sehir            = models.ForeignKey(Sehir,on_delete=models.CASCADE)
    restaurantAdi    = models.CharField(max_length=100)
    restaurantYildiz = models.CharField(max_length=10)
    konumX           = models.FloatField()
    konumY           = models.FloatField()

    def __str__(self):
        return self.restaurantAdi