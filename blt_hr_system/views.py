from django.urls import reverse
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from . import models
from . import forms
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

def home(request):
    return render(request, 'home.html')

def account(request):
    return render(request, 'account.html')

def delete_training_doc(request):
    if request.method == 'POST':
        form = forms.training_docs_submit(request.POST)
        if form.is_valid():
            documents = models.training_docs.objects.all()
            document_name = request.POST.get('document_name') 
            item = models.training_docs.objects.get(upload_name=document_name)       
            item.delete()
            return HttpResponseRedirect(reverse('admin'))
    form = forms.remove_doc()
    documents = models.training_docs.objects.all()
    context = {'documents': documents,
                'form': form,}
    return render(request, 'delete_training_doc.html', context)    

def training_material(request):
    if request.method == 'POST':
        form = forms.training_docs_submit(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.uploaded_by = request.user
            obj.save()
            return HttpResponseRedirect(reverse('admin'))
    documents = models.training_docs.objects.all()
    form = forms.training_docs_submit()
    context = {'documents': documents,
                'form': form,}
    return render(request, 'training_material.html', context)

def certification_request(request):
    if request.method == 'POST':
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
    documents = models.training_docs.objects.all()
    documents = documents.order_by('upload_name')
    context = {'documents': documents,}
    return render(request, 'training_center.html', context)

def employee_group(request):
    employee_group = models.employee_group.objects.all()
    emptyCourses = False
    if not employee_group:
        emptyCourses = True
    context = {'employee_group': employee_group}
    return render(request, 'employee_groups.html', context)

def cert_groups(request):
    return render(request, 'cert_groups.html')

def performance_reviews(request):
    return render(request, 'performance_reviews.html')

def admin(request):
    return render(request, 'admin.html')