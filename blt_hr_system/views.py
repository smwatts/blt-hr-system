from django.urls import reverse
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from . import models
from . import forms
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.models import User

def home(request):
    return render(request, 'home.html')

def account(request):
    return render(request, 'account.html')

def managed_certs(request):
    if request.method == 'POST':
        cert_form = forms.add_certification(request.POST)
        cert_form.save()
        return HttpResponseRedirect(reverse('admin'))
    else:
        cert_form = forms.add_certification()
        cert_info = models.certification.objects.all()
        context = {'cert_form': cert_form,
                   'cert_info' : cert_info}
    return render(request, 'managed_certs.html', context)

def certifications(request):
    cert_info = models.certification.objects.all()
    context = {'cert_info' : cert_info}
    return render(request, 'certifications.html', context)

@transaction.atomic
def update_profile(request, pk):
    if request.method == 'POST':
        user_account = User.objects.get(id=pk)
        user_form = forms.UserForm(request.POST, instance=user_account)
        profile_form = forms.ProfileForm(request.POST, instance=user_account.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'The employee profile was successfully updated!')
            return HttpResponseRedirect(reverse('admin'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_account = User.objects.get(id=pk)
        user_form = forms.UserForm(instance=user_account)
        profile_form = forms.ProfileForm(instance=user_account.profile)
    return render(request, 'edit_employee_info.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def employee_directory(request):
    users = User.objects.all().order_by('first_name', 'last_name')
    # only include users where "profile.is_active=True"
    context = {'users' : users}
    return render(request, 'employee_directory.html', context)

def company_locations(request):
    locations = models.company_info.objects.all().order_by('location')
    # only include users where "profile.is_active=True"
    context = {'locations' : locations}
    return render(request, 'company_locations.html', context)

def employee_directory_edit(request):
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'employee_directory_edit.html', context)

def signup(request):
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.refresh_from_db()  # load the profile instance created by the signal
            obj.profile.start_date = request.POST['start_date']
            obj.profile.save()
            return HttpResponseRedirect(reverse('admin'))
    else:
        form = forms.SignUpForm()
    return render(request, 'signup.html', {'form': form})

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

def add_company_info(request):
    if request.method == 'POST':
        company_info_form = forms.submit_company_info(request.POST)
        company_info_form.save()
        return HttpResponseRedirect(reverse('admin'))
    else:
        company_info_form = forms.submit_company_info()
        company_info = models.company_info.objects.all()
        context = {'company_info_form': company_info_form,
                   'company_info' : company_info}
        return render(request, 'add_company_info.html', context)

@transaction.atomic
def edit_company_info(request, pk):
    if request.method == 'POST':
        company_info = models.company_info.objects.get(id=pk)
        info_form = forms.submit_company_info(request.POST, instance=company_info)
        if info_form.is_valid():
            info_form.save()
            messages.success(request, 'The location information was successfully updated!')
            return HttpResponseRedirect(reverse('admin'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        company_info = models.company_info.objects.get(id=pk)
        info_form = forms.submit_company_info(instance=company_info)
        context = {'info_form': info_form,
                   }
        return render(request, 'edit_company_info.html', context)

def training_center(request):
    documents = models.training_docs.objects.all()
    documents = documents.order_by('upload_name')
    context = {'documents': documents,}
    return render(request, 'training_center.html', context)

def performance_reviews(request):
    return render(request, 'performance_reviews.html')

def admin(request):
    return render(request, 'admin.html')