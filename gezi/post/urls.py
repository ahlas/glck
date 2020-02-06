from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    #Burada view.py de bulunan fonksiyonu çalıştırmış oluyor.
    url(r'^$', views.homePageView, name='index'),
    url(r'detail/', views.detail, name='detail'),
    #url(r'^(\d+)/$', views.result, name='result')
    path('<str:sehirAdi>/<int:sehirID>/', views.result, name='result')
]