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
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')

def account(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    return render(request, 'account.html')

def edit_system_certs(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        cert = models.certification.objects.get(id=pk)
        certs_form = forms.add_certification(request.POST, instance=cert)
        if certs_form.is_valid():
            messages.success(request, 'The certification was successfully updated!')
            certs_form.save()
            return HttpResponseRedirect(reverse('certifications'))
    else:
        cert = models.certification.objects.get(id=pk)
        certs_form = forms.add_certification(instance=cert)
        context = {'certs_form': certs_form,}
    return render(request, 'edit_system_certs.html', context)

def employee_required_certs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'employee_required_certs.html', context)

def add_birth_date(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        birth_date = forms.add_birth_date(request.POST, instance=request.user.profile)
        if birth_date.is_valid():
            birth_date.save()
            messages.success(request, 'Your birth dates was successfully updated!')
            return HttpResponseRedirect(reverse('account'))
    else:
        birth_date = forms.add_birth_date(instance=request.user.profile)
        context = {'birth_date':birth_date}
    return render(request, 'add_birth_date.html', context)

def managed_certs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        cert_form = forms.add_certification(request.POST)
        cert_form.save()
        return HttpResponseRedirect(reverse('certifications'))
    else:
        cert_form = forms.add_certification()
        cert_info = models.certification.objects.all()
        context = {'cert_form': cert_form,
                   'cert_info' : cert_info}
    return render(request, 'managed_certs.html', context)

def certifications(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    cert_info = models.certification.objects.all().order_by('name')
    context = {'cert_info' : cert_info}
    return render(request, 'certifications.html', context)

@transaction.atomic
def update_profile(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        user_account = User.objects.get(id=pk)
        user_form = forms.UserForm(request.POST, instance=user_account)
        profile_form = forms.ProfileForm(request.POST, instance=user_account.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'The employee profile was successfully updated!')
            return HttpResponseRedirect(reverse('employee_directory_edit'))
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

@transaction.atomic
def edit_required_certs(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        user_account = User.objects.get(id=pk)
        certs_form = forms.edit_system_certs(request.POST, instance=user_account.profile)
        if certs_form.is_valid():
            obj = certs_form.save()
            obj.certs.set(request.POST.getlist('certs'))
            obj.save()
            messages.success(request, 'The employee certifications were successfully updated!')
            return HttpResponseRedirect(reverse('employee_required_certs'))
    else:
        user_account = User.objects.get(id=pk)
        certs_form = forms.edit_system_certs(instance=user_account.profile)
        context = {'user_account': user_account,
                    'certs_form': certs_form,}
        return render(request, 'edit_required_certs.html', context)

def employee_directory(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    users = User.objects.all().filter(is_active=True).exclude(username='system_admin').order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'employee_directory.html', context)

def company_locations(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    locations = models.company_info.objects.all().order_by('location')
    context = {'locations' : locations}
    return render(request, 'company_locations.html', context)

def employee_directory_edit(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.username != "system_admin":
        return redirect('home')
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'employee_directory_edit.html', context)

def signup(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        print(form)
        if form.is_valid():
            # submit employee informatation to create an account with profile information
            obj = form.save()
            obj.refresh_from_db() 
            obj.profile.start_date = request.POST['start_date']
            profile_instance = models.Profile.objects.get(pk=request.POST['manager'])
            obj.profile.manager = profile_instance
            location_instance = models.company_info.objects.get(pk=request.POST['location'])
            obj.profile.location = location_instance
            obj.profile.position = request.POST['position']
            obj.profile.certs.set(request.POST.getlist('certifications'))
            obj.profile.save()
            # send an email to the user to let them know that their account has been setup
            password = request.POST['password1']
            username = request.POST['username']
            domain = request.META['HTTP_HOST']
            mail_subject = 'Welcome to your BLT HR System.'
            message = render_to_string('acc_active_email.html', {
                'username': username,
                'password': password,
                'domain': domain,
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponseRedirect(reverse('employee_directory_edit'))
    else:
        form = forms.SignUpForm()
    return render(request, 'signup.html', {'form': form})

def delete_training_doc(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.training_docs_submit(request.POST)
        if form.is_valid():
            documents = models.training_docs.objects.all()
            document_name = request.POST.get('document_name') 
            item = models.training_docs.objects.get(upload_name=document_name)       
            item.delete()
            return HttpResponseRedirect(reverse('training_center'))
    form = forms.remove_doc()
    documents = models.training_docs.objects.all()
    context = {'documents': documents,
                'form': form,}
    return render(request, 'delete_training_doc.html', context)    

def training_material(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.training_docs_submit(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.uploaded_by = request.user
            obj.save()
            return HttpResponseRedirect(reverse('training_center'))
    documents = models.training_docs.objects.all()
    form = forms.training_docs_submit()
    context = {'documents': documents,
                'form': form,}
    return render(request, 'training_material.html', context)

def certification_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('home'))
    else:
        cert_request = forms.cert_request()
    context = {'cert_request': cert_request}
    return render(request, 'certification_request.html', context)

def absence_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('home'))
    else:
        absence_form = forms.absence_request()
    context = {'absence_form': absence_form}
    return render(request, 'absence_request.html', context)

def add_company_info(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        company_info_form = forms.submit_company_info(request.POST)
        company_info_form.save()
        return HttpResponseRedirect(reverse('company_locations'))
    else:
        company_info_form = forms.submit_company_info()
        company_info = models.company_info.objects.all()
        context = {'company_info_form': company_info_form,
                   'company_info' : company_info}
        return render(request, 'add_company_info.html', context)

@transaction.atomic
def edit_company_info(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        company_info = models.company_info.objects.get(id=pk)
        info_form = forms.submit_company_info(request.POST, instance=company_info)
        if info_form.is_valid():
            info_form.save()
            messages.success(request, 'The location information was successfully updated!')
            return HttpResponseRedirect(reverse('company_locations'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        company_info = models.company_info.objects.get(id=pk)
        info_form = forms.submit_company_info(instance=company_info)
        context = {'info_form': info_form,
                   }
        return render(request, 'edit_company_info.html', context)

def training_center(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    documents = models.training_docs.objects.all()
    documents = documents.order_by('upload_name')
    context = {'documents': documents,}
    return render(request, 'training_center.html', context)

def performance_reviews(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    return render(request, 'performance_reviews.html')

def admin(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'admin.html')