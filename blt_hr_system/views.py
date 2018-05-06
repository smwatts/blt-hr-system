from django.urls import reverse
from django.template import loader, RequestContext
from django.shortcuts import render
from . import models
from . import forms

def home(request):
    return render(request, 'home.html')

def certification_request(request):
    cert_request = forms.cert_request()
    context = {'cert_request': cert_request}
    return render(request, 'certification_request.html', context)

def absence_request(request):
    absence_form = forms.absence_request()
    context = {'absence_form': absence_form}
    return render(request, 'absence_request.html', context)

def training_center(request):
    return render(request, 'training_center.html')

def employee_groups(request):
    return render(request, 'employee_groups.html')

def cert_groups(request):
    return render(request, 'cert_groups.html')