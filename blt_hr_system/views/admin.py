from django.urls import reverse
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
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

# General function to list all company locations
def company_locations(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    locations = models.company_info.objects.all().order_by('location')
    context = {'locations' : locations,
                'system_access':system_access,
    }
    return render(request, 'admin/company_locations.html', context)

# ------------------------------------------------------------------
# EMPLOYEE FUNCTIONS
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------

# Admin function to access the main page for all admin controls
def admin(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
        return HttpResponseRedirect(reverse('home'))
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    all_user_tf = False
    if all_user.exists():
        all_user_tf = True
    abs_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Absences')
    abs_user_tf = False
    if abs_user.exists():
        abs_user_tf = True
    cert_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Certifications')
    cert_user_tf = False
    if cert_user.exists():
        cert_user_tf = True
    doc_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Documents')
    doc_user_tf = False
    if doc_user.exists():
        doc_user_tf = True
    train_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Training')
    train_user_tf = False
    if train_user.exists():
        train_user_tf = True
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    perf_user_tf = False
    if perf_user.exists():
        perf_user_tf = True
    ts_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Timesheets')
    ts_user_tf = False
    if ts_user.exists():
        ts_user_tf = True
    dir_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Directory')
    dir_user_tf = False
    if dir_user.exists():
        dir_user_tf = True
    context = {'system_access':system_access,
                'dir_user_tf':dir_user_tf,
                'ts_user_tf':ts_user_tf,
                'perf_user_tf':perf_user_tf,
                'train_user_tf':train_user_tf,
                'doc_user_tf':doc_user_tf,
                'cert_user_tf':cert_user_tf,
                'abs_user_tf':abs_user_tf,
                'all_user_tf':all_user_tf,
    }
    return render(request, 'admin/admin.html', context)

def account_access(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    if request.user.username != "system_admin" and not all_user.exists():
        return HttpResponseRedirect(reverse('home'))
    # to do: add a list of employees and their access levels
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {'users' : users,
                'system_access':system_access
    }
    return render(request, 'admin/account_access.html', context)

@transaction.atomic
def account_access_update(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    if request.user.username != "system_admin" and not all_user.exists():
        return HttpResponseRedirect(reverse('home'))
    context = {}
    if request.method == 'POST':
        user_account = User.objects.get(id=pk)
        form = forms.edit_system_access(request.POST, instance=user_account.profile)
        user_account.profile.access.set(request.POST.getlist('access'))
        messages.success(request, 'The employee access was successfully updated!')
        return HttpResponseRedirect(reverse('account_access'))
    else:
        user_account = User.objects.get(id=pk)
        form = forms.edit_system_access(instance=user_account.profile)
        context = {'user_account': user_account,
                    'form': form,
                    'system_access':system_access}
    return render(request, 'admin/account_access_update.html', context)

# Admin function to create company locations
def add_company_info(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    if request.user.username != "system_admin" and not all_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        company_info_form = forms.submit_company_info(request.POST)
        company_info_form.save()
        return HttpResponseRedirect(reverse('add_company_info'))
    else:
        company_info_form = forms.submit_company_info()
        company_info = models.company_info.objects.all().order_by('location')
        context = {'company_info_form': company_info_form,
                   'company_info' : company_info,
                   'system_access':system_access}
        return render(request, 'admin/add_company_info.html', context)

# Admin function to edit the locations of the company
@transaction.atomic
def edit_company_info(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    if request.user.username != "system_admin" and not all_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        company_info = models.company_info.objects.get(id=pk)
        info_form = forms.submit_company_info(request.POST, instance=company_info)
        if info_form.is_valid():
            info_form.save()
            messages.success(request, 'The location information was successfully updated!')
            return HttpResponseRedirect(reverse('add_company_info'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        company_info = models.company_info.objects.get(id=pk)
        info_form = forms.submit_company_info(instance=company_info)
        context = {'info_form': info_form,
                   'system_access':system_access}
        return render(request, 'admin/edit_company_info.html', context)
