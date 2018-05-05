from django.urls import reverse
from django.template import loader, RequestContext
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def certification_request(request):
    return render(request, 'certification_request.html')

def absence_request(request):
    return render(request, 'absence_request.html')

def training_center(request):
    return render(request, 'training_center.html')