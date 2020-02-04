from django.contrib import admin
from .models import Sehir, AltSehir

#Admin panelinde de modelimizin görülmesini,değişiklik yapılabilir olmasını istiyorsak burada onu belirtiyoruz
# Register your models here.
admin.site.register(Sehir)
admin.site.register(AltSehir)
