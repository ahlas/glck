from django.shortcuts import render,HttpResponse
from django.shortcuts import render_to_response


def home_view(request):
    return render(request,'firstPage.html')


