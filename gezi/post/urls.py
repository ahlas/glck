from django.conf.urls import url
from . import views

urlpatterns = [
    #Burada view.py de bulunan fonksiyonu çalıştırmış oluyor.
    url(r'^$', views.homePageView, name='index'),
    url(r'updateCityFiltered/', views.updateCityFiltered, name='updateCity'),
    url(r'detail/', views.detail, name='detail'),
    url(r'result/', views.result, name='result'),
]