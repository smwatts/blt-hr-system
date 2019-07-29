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
    locations = models.company_info.objects.all().order_by('location')
    context = {'locations' : locations}
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
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'admin/admin.html')

def account_access(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    account_access_form = forms.account_access_form()
    context = {'account_access_form':account_access_form}
    return render(request, 'admin/account_access.html', context)  

# Admin function to create company locations
def add_company_info(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        company_info_form = forms.submit_company_info(request.POST)
        company_info_form.save()
        return HttpResponseRedirect(reverse('add_company_info'))
    else:
        company_info_form = forms.submit_company_info()
        company_info = models.company_info.objects.all().order_by('location')
        context = {'company_info_form': company_info_form,
                   'company_info' : company_info}
        return render(request, 'admin/add_company_info.html', context)

# Admin function to edit the locations of the company
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
        return render(request, 'admin/edit_company_info.html', context)
