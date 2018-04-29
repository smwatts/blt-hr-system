from django.urls import reverse
from django.template import loader, RequestContext
from django.shortcuts import render

def home(request):
    return render(request, 'blt_hr_system/home.html')