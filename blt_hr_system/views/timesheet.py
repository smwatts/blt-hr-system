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
    if request.method == 'POST':
            form = forms.upload_jobs(request.POST, request.FILES)
            errors = []
            if form.is_valid():
                file = request.FILES['docfile']
                # first check to make sure a csv has been uploaded
                if file.name.split('.')[-1] != 'csv':
                    upload_jobs = forms.upload_jobs()
                    sage_jobs = models.sage_jobs.objects.all()
                    context = {'upload_jobs':upload_jobs,
                                'errors': errors,
                                'sage_jobs':sage_jobs}
                    errors.append('The file extension must end in .csv.')
                    return render(request, 'timesheet/jobs_upload.html', context)
                else:
                    # then check to make sure the csv is in the correct format
                    df = pd.read_csv(request.FILES['docfile'])
                    try:
                        # check a few conditions to make sure the date is ok
                        if df.count()[0] == df.count()[1]:
                            sage_jobs = pd.DataFrame(list(models.sage_jobs.objects.all().values('job_id', 'job_desc')))
                            if len(sage_jobs.index) < 1:
                                sage_jobs = pd.DataFrame(columns=['job_id', 'job_desc'])
                            job_id_lst = sage_jobs['job_id'].tolist()
                            df = df[~(df["Job"].isin(job_id_lst))]
                            for row in df.itertuples():
                                # TO DO: only add if the value does not exist in the db
                                row = models.sage_jobs.objects.create(job_id=row.Job, job_desc=row.Description)
                            return redirect('jobs_upload')
                        else:
                            upload_jobs = forms.upload_jobs()
                            sage_jobs = models.sage_jobs.objects.all()
                            context = {'upload_jobs':upload_jobs,
                                        'errors': errors,
                                        'sage_jobs':sage_jobs}
                            errors.append('There was an error in the uploaded csv. Please ensure:')
                            errors.append('You have a "Job" and "Description" column.')
                            errors.append('Both columns are the same length.')
                            return render(request, 'timesheet/jobs_upload.html', context)
                    except:
                        upload_jobs = forms.upload_jobs()
                        sage_jobs = models.sage_jobs.objects.all()
                        context = {'upload_jobs':upload_jobs,
                                    'errors': errors,
                                    'sage_jobs':sage_jobs}
                        errors.append('There was an error in the uploaded csv. Please ensure:')
                        errors.append('You have a "Job" and "Description" column.')
                        errors.append('Both columns are the same length.')
                        return render(request, 'timesheet/jobs_upload.html', context)
            else:
                upload_jobs = forms.upload_jobs()
                errors = []
                context = {'upload_jobs':upload_jobs,
                            'errors': errors}
                return render(request, 'timesheet/jobs_upload.html', context)
    upload_jobs = forms.upload_jobs()
    errors = []
    sage_jobs = models.sage_jobs.objects.all().order_by('job_id')
    context = {'upload_jobs':upload_jobs,
                'errors': errors,
                'sage_jobs':sage_jobs}
    return render(request, 'timesheet/jobs_upload.html', context)

# Admin function to edit the descriptions of job IDs
def job_upload_edit(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        sage_job = models.sage_jobs.objects.get(id=pk)
        sage_form = forms.sage_job_update(request.POST, instance=sage_job)
        if sage_form.is_valid():
            sage_form.save()
            return HttpResponseRedirect(reverse('jobs_upload'))
        else:
            messages.error(request, 'Please correct the error below.')
    sage_job = models.sage_jobs.objects.get(id=pk)
    sage_form = forms.sage_job_update(instance=sage_job)
    context = {'sage_form':sage_form}
    return render(request, 'timesheet/job_upload_edit.html', context)

# Admin function to view the status of employee timesheets
def timesheet_status(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {}
    return render(request, 'timesheet/timesheet_status.html', context)

# Admin function to view timesheet_home for each employee
def admin_timesheet_home(request):
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
