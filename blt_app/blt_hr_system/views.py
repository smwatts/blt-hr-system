from django.urls import reverse
from django.template import loader, RequestContext
from django.shortcuts import render

def submit_cert(request):
    return render(request, 'blt_hr_system/submit_cert.html')