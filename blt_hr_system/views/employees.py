from django.urls import reverse
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from .. import models
from .. import forms
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import datetime
import datedelta
from django.db.models import Q
from collections import defaultdict
from django.db import connection

# -----------------------------------------------------------------
# GENERAL/HELPER FUNCTIONS
# -----------------------------------------------------------------

# General function to create an employee directory
def employee_directory(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    users = User.objects.all().filter(is_active=True).exclude(username='system_admin').order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'employees/employee_directory.html', context)

# ------------------------------------------------------------------
# EMPLOYEE FUNCTIONS
# ------------------------------------------------------------------

# Employee function to display account information
def account(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    ack_docs = list(models.doc_read_req.objects.all().filter(employee=request.user).values('doc__name'))
    sub_docs = list(models.doc_submit_req.objects.all().filter(employee=request.user).values('doc__name'))
    context = {'ack_docs':ack_docs,
                'sub_docs':sub_docs,
    }
    return render(request, 'employees/account.html', context)

# Employee function to add a day of birth to their account
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

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------

# Admin function to create a new employee account
def signup(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        print(form)
        if form.is_valid():
            print('valid')
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
            message = render_to_string('employees/acc_active_email.html', {
                'username': username,
                'password': password,
                'domain': domain,
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
    else:
        form = forms.SignUpForm()
    return render(request, 'employees/signup.html', {'form': form})

# Admin function used to display all employee information
# Links to the employee edit page
def employee_directory_edit(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.username != "system_admin":
        return redirect('home')
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'employees/employee_directory_edit.html', context)

# Admin function used to edit an individual employee's information
# TO DO: Add in the ability to change an employees start date
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
    return render(request, 'employees/edit_employee_info.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
