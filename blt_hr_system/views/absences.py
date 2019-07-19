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
import pandas as pd
import csv
import datetime
import datedelta

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
    if 'export_holidays' in request.POST:
        return export_holidays()
    now = datetime.datetime.now()
    upcoming_holidays = models.company_holidays.objects.all().filter(is_finalized=True, 
        holiday_date__gte=now).values('holiday_date', 'holiday_name', 
        'location').order_by('holiday_date', 'location')
    control_date = models.control_date.objects.all().order_by('location')
    context = {'control_date': control_date,
               'upcoming_holidays': company_holidays,}
    return render(request, 'absences/add_company_holidays.html', context)

# Admin function used to export all historical and upcoming company holidays
def export_holidays():
    df = pd.DataFrame((list(models.company_holidays.objects.all().values('holiday_date', 'holiday_name'))))
    if len(df.index) > 0:
        df = df.sort_values(by=['holiday_date', 'location'])
        df = df[['holiday_name', 'holiday_date']]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=company_holidays.csv'
    df.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
    return response

# Admin function to set last holiday date
def upload_holidays(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        print('made it here')
        form = forms.upload_holidays(request.POST, request.FILES)
        if form.is_valid():
            # return the validate page
            context={'pk': 1}
            return render(request, 'absences/validate_holidays.html', context)
        else:
            upload_holidays = forms.upload_holidays()
            errors = []
            context = {'upload_holidays':upload_holidays,
                        'errors': errors}
            return render(request, 'absences/upload_holidays.html')
    else:
        upload_holidays = forms.upload_holidays()
        errors = []
        context = {'upload_holidays':upload_holidays,
                'errors': errors}
        return render(request, 'absences/upload_holidays.html', context)

# Admin function to set last holiday date
def validate_holidays(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'absences/validate_holidays.html', context)

# Admin function to set last holiday date
def last_absence_date(request, pk):
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
