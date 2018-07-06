from django.urls import reverse
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from . import models
from . import forms

def home(request):
    return render(request, 'home.html')

def certification_request(request):
    if request.method == 'POST':
        # cert_request = forms.cert_request(request.POST)
        # cert_request.save()
        return HttpResponseRedirect(reverse('home'))
    else:
        cert_request = forms.cert_request()
    context = {'cert_request': cert_request}
    return render(request, 'certification_request.html', context)

def absence_request(request):
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('home'))
    else:
        absence_form = forms.absence_request()
    context = {'absence_form': absence_form}
    return render(request, 'absence_request.html', context)

def add_employee_group(request):
    if request.method == 'POST':
        employee_group = forms.add_employee_group(request.POST)
        employee_group.save()
        return HttpResponseRedirect(reverse('admin'))
    else:
        add_emp_group = forms.add_employee_group()
    context = {'add_emp_group': add_emp_group}
    return render(request, 'add_employee_group.html', context)

def training_center(request):
    return render(request, 'training_center.html')

def employee_group(request):
    # Stuck here - can't grab all from employee_group
    # Could be a problem initializing the table
    employee_group = models.employee_group.objects.all()
    emptyCourses = False
    if not employee_group:
        emptyCourses = True
    context = {'employee_group': employee_group,
               'emptyCourses': emptyCourses}
    return render(request, 'employee_groups.html', context)

def cert_groups(request):
    return render(request, 'cert_groups.html')

def performance_reviews(request):
    return render(request, 'performance_reviews.html')

def admin(request):
    return render(request, 'admin.html')