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
import random
from django.db.models.aggregates import Max

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
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('home'))
    else:
        absence_form = forms.absence_request()
    context = {'absence_form': absence_form,
                'system_access': system_access,
    }
    return render(request, 'absences/absence_request.html', context)

# Employee function to review absence requests
def review_absence_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    context = {'system_access':system_access}
    return render(request, 'absences/review_absence_request.html', context)

# Employee function to view company holidays
def company_holidays(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    context = {'system_access':system_access}
    return render(request, 'absences/company_holidays.html', context)

# Employee function to view employees taking holiday time
def employee_absences(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    context = {'system_access':system_access}
    return render(request, 'absences/employee_absences.html', context)

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------

# Admin function to view & add company holidays
# Admin can also access the 'last date to book absence requests' here
def add_company_holidays(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    abs_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Absences')
    if request.user.username != "system_admin" and not all_user.exists() and not abs_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if 'export_holidays' in request.POST:
        return export_holidays()
    now = datetime.datetime.now()
    upcoming_holidays = models.company_holidays.objects.filter(is_finalized=True, 
        holiday_date__gte=now).order_by('holiday_date', 'location')
    control_date = models.company_holidays.objects.all().filter(is_finalized=True) \
        .values('location__location') \
        .annotate(max_holiday_date=Max('holiday_date'))

    context = {'control_date': control_date,
               'upcoming_holidays': upcoming_holidays,
                'system_access': system_access,}
    return render(request, 'absences/add_company_holidays.html', context)

# Admin function used to export all historical and upcoming company holidays
def export_holidays():
    df = pd.DataFrame((list(models.company_holidays.objects.all().values('holiday_date', 'holiday_name', 'location__location') \
        .filter(is_finalized=True))))
    if len(df.index) > 0:
        df = df.sort_values(by=['holiday_date', 'location__location'])
        df = df[['holiday_name', 'holiday_date', 'location__location']]
        df = df.rename(columns={"location__location": "location"})
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=company_holidays.csv'
    df.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
    return response

# Admin function to set last holiday date
def upload_holidays(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    abs_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Absences')
    if request.user.username != "system_admin" and not all_user.exists() and not abs_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.upload_holidays(request.POST, request.FILES)
        errors = []
        if form.is_valid():
            file = request.FILES['docfile']
            # first check to make sure a csv has been uploaded
            if file.name.split('.')[-1] != 'csv':
                upload_holidays = forms.upload_holidays()
                context = {'upload_holidays':upload_holidays,
                        'errors': errors,
                         'system_access': system_access,}
                errors.append('The file extension must end in .csv.')
                return render(request, 'absences/upload_holidays.html', context)
            else:
                # then check to make sure the csv is in the correct format
                df = pd.read_csv(request.FILES['docfile'])
                # get the location for the upload
                loc = request.POST.get('location')                
                # check to make sure that all holidays are after the holidays already submitted
                test_date = datetime.date(1990, 1, 1)
                df_date = pd.DataFrame(list(models.company_holidays.objects.all().values('holiday_date').filter(location=loc)))
                # if there is already date info in the model then we'll need to update the test date
                if len(df_date.index) > 0:
                    test_date = max(df_date['holiday_date'])
                try:
                    # try to convert date to date field
                    df['Date'] = df['Date'].astype('datetime64[ns]')
                    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d").dt.date
                    # check a few conditions to make sure the date is ok
                    if df.count()[0] == df.count()[1] and df.count()[1] > 0 and max(df['Date']) > test_date:
                        val = random.randrange(100000)
                        df['val'] = val
                        df['is_finalized'] = False
                        for row in df.itertuples():
                            row = models.company_holidays.objects.create(holiday_name=row.Holiday, holiday_date=row.Date, 
                                location_id=loc, is_finalized=row.is_finalized, upload_id=row.val)
                        return redirect('validate_holidays', pk=val)
                    else:
                        upload_holidays = forms.upload_holidays()
                        context = {'upload_holidays':upload_holidays,
                                'errors': errors,
                                 'system_access': system_access,}
                        errors.append('There was an error in the uploaded csv. Please ensure:')
                        errors.append('You have a "Holiday" and "Date" column.')
                        errors.append('Both columns are the same length.')
                        errors.append('"Date" column only contains dates.')
                        errors.append('No dates are prior to the most recent uploaded date.')
                        
                        return render(request, 'absences/upload_holidays.html', context)
                except:
                    upload_holidays = forms.upload_holidays()
                    context = {'upload_holidays':upload_holidays,
                            'errors': errors,
                             'system_access': system_access,}
                    errors.append('There was an error in the uploaded csv. Please ensure:')
                    errors.append('You have a "Holiday" and "Date" column.')
                    errors.append('Both columns are the same length.')
                    errors.append('"Date" column only contains dates.')
                    errors.append('No dates are prior to the most recent uploaded date.')
                    
                    return render(request, 'absences/upload_holidays.html', context)
        else:
            upload_holidays = forms.upload_holidays()
            errors = []
            context = {'upload_holidays':upload_holidays,
                        'errors': errors,
                         'system_access': system_access,}
            return render(request, 'absences/upload_holidays.html', context)
    else:
        upload_holidays = forms.upload_holidays()
        errors = []
        context = {'upload_holidays':upload_holidays,
                'errors': errors,
                 'system_access': system_access,}
        return render(request, 'absences/upload_holidays.html', context)

# Admin function to set last holiday date
def validate_holidays(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    abs_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Absences')
    if request.user.username != "system_admin" and not all_user.exists() and not abs_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        if 'cancel' in request.POST:
            models.company_holidays.objects.filter(upload_id=pk).delete()
            return HttpResponseRedirect(reverse('add_company_holidays'))
        else:
            models.company_holidays.objects.filter(upload_id=pk).update(is_finalized=True)
            return HttpResponseRedirect(reverse('add_company_holidays'))
    else:
        holiday_val = models.company_holidays.objects.filter(upload_id=pk)
        context = {'holiday_val':holiday_val,
         'system_access': system_access,}
        return render(request, 'absences/validate_holidays.html', context)

# Admin function to edit company holidays
def edit_company_holiday(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    abs_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Absences')
    if request.user.username != "system_admin" and not all_user.exists() and not abs_user.exists():
        return HttpResponseRedirect(reverse('home'))
    context = { 'system_access': system_access,}
    return render(request, 'absences/edit_company_holiday.html', context)

# Admin function to view absence requests
def view_absence_requests(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    abs_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Absences')
    if request.user.username != "system_admin" and not all_user.exists() and not abs_user.exists():
        return HttpResponseRedirect(reverse('home'))
    context = { 'system_access': system_access,}
    return render(request, 'absences/view_absence_requests.html', context)

# Admin function to approve individual absence requests
def approve_absence_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    abs_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Absences')
    if request.user.username != "system_admin" and not all_user.exists() and not abs_user.exists():
        return HttpResponseRedirect(reverse('home'))
    context = { 'system_access': system_access,}
    return render(request, 'absences/approve_absence_request.html', context)
