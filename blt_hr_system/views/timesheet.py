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

# ------------------------------------------------------------------
# EMPLOYEE FUNCTIONS
# ------------------------------------------------------------------

# Employee function to view all timesheets
def timesheet_home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    context = {}
    return render(request, 'timesheet/timesheet_home.html', context)

# Employee function to view complete a specific timesheet
def timesheet(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    context = {}
    return render(request, 'timesheet/timesheet.html', context)

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------

# Admin function to upload job ID's
def jobs_upload(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'timesheet/jobs_upload.html', context)

# Admin function to view the status of employee timesheets
def timesheet_status(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'timesheet/timesheet_status.html', context)

# Admin function to view timesheet_home for each employee
def admin_timesheet_home(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'timesheet/admin_timesheet_home.html', context)

# Admin function to view a particular timesheet for a particular employee
def admin_timesheet(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'timesheet/admin_timesheet.html', context)

# Admin function to export timesheets
def export_timesheets(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'timesheet/export_timesheets.html', context)
