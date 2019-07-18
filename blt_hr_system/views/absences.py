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

# ------------------------------------------------------------------
# EMPLOYEE FUNCTIONS
# ------------------------------------------------------------------

# Employee function to submit an absence request
def absence_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('home'))
    else:
        absence_form = forms.absence_request()
    context = {'absence_form': absence_form}
    return render(request, 'absences/absence_request.html', context)

# Employee function to review absence requests
def review_absence_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    context = {}
    return render(request, 'absences/review_absence_request.html', context)

# Employee function to view company holidays
def company_holidays(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    context = {}
    return render(request, 'absences/company_holidays.html', context)

# Employee function to view employees taking holiday time
def employee_absences(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    context = {}
    return render(request, 'absences/employee_absences.html', context)

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------

# Admin function to view & add company holidays
# Admin can also access the 'last date to book absence requests' here
def add_company_holidays(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'absences/add_company_holidays.html', context)

# Admin function to set last holiday date
def last_absence_date(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'absences/last_absence_date.html', context)

# Admin function to edit company holidays
def edit_company_holiday(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'absences/edit_company_holiday.html', context)

# Admin function to view absence requests
def view_absence_requests(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'absences/view_absence_requests.html', context)

# Admin function to approve individual absence requests
def approve_absence_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'absences/approve_absence_request.html', context)
