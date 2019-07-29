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
import datetime
import pandas as pd
import csv

# -----------------------------------------------------------------
# GENERAL/HELPER FUNCTIONS
# -----------------------------------------------------------------

# ------------------------------------------------------------------
# EMPLOYEE FUNCTIONS
# ------------------------------------------------------------------

# Employee function to view performance reviews
def performance_reviews(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    user = request.user.id
    if request.method == 'POST':
        file_form = forms.submit_perf(request.POST, request.FILES)
        if file_form.is_valid():
            obj = file_form.save(commit=False)
            obj.employee_id = user
            obj.save()
            messages.success(request, 'The form was successfully uploaded!')
            return HttpResponseRedirect(reverse('performance_reviews'))
        else:
            messages.error(request, 'Please correct the error below.')
            return HttpResponseRedirect(reverse('performance_reviews'))
    perf_type = models.Profile.objects.values_list('perf_cat', flat=True).get(id=user)
    perf_required = False
    req_perf = None
    if perf_type is not None:
        req_perf = models.perf_forms.objects.all().filter(perf_cat=str(perf_type)) \
            .order_by('-uploaded_at')[:1].values('upload', 'upload_name')
        if req_perf.exists():
            perf_required = True
        else:
            perf_required = False
    year = datetime.date.today().year
    month = datetime.date.today().month
    if month < 11:
        year = year - 1
    last_uploaded = models.emp_perf_forms.objects.all().filter(employee=user, year=year)
    upload_req = True
    if last_uploaded.exists():
        upload_req = False
    completed_forms = models.emp_perf_forms.objects.all().filter(employee=user).order_by('uploaded_at')
    manager = False
    manager_qs = models.Profile.objects.all().filter(manager_id=user).exclude(perf_cat=None)
    if manager_qs.exists():
        manager = True
    form = forms.submit_perf()
    context = {'req_perf':req_perf,
                'perf_required':perf_required,
                'completed_forms':completed_forms,
                'form':form,
                'upload_req':upload_req,
                'year':year,
                'manager':manager,
                'system_access':system_access,
    }
    return render(request, 'performance/performance_reviews.html', context)

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------
def add_edit_perf_cat(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    if request.user.username != "system_admin" and not all_user.exists() and not perf_user.exists():
        return HttpResponseRedirect(reverse('home'))
    perf_cat = models.Profile.objects.all().order_by('user__first_name', 'user__last_name')
    context = {'perf_cat': perf_cat,}
    return render(request, 'performance/add_edit_perf_cat.html', context)

def edit_emp_perf_cat(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    if request.user.username != "system_admin" and not all_user.exists() and not perf_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        perf_form = models.Profile.objects.get(id=pk)
        info_form = forms.edit_emp_perf_cat(request.POST, instance=perf_form)
        if info_form.is_valid():
            info_form.save()
            messages.success(request, 'The form was successfully updated!')
            return HttpResponseRedirect(reverse('add_edit_perf_cat'))
        else:
            messages.error(request, 'Please correct the error below.')
            return HttpResponseRedirect(reverse('add_edit_perf_cat'))
    else:
        perf_form = models.Profile.objects.get(id=pk)
        info_form = forms.edit_emp_perf_cat(instance=perf_form)
        context = {'info_form': info_form,
                   'perf_form': perf_form,
                   'system_access':system_access,}
    return render(request, 'performance/edit_emp_perf_cat.html', context)

# Admin function to add, view and edit performance review forms
def add_perf_forms(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    if request.user.username != "system_admin" and not all_user.exists() and not perf_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.perf_forms_submit(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect(reverse('add_perf_forms'))
    cats = models.perf_forms.objects.all().exclude(perf_cat_id=None).values_list('perf_cat_id', flat=True)
    if cats.exists():
        cats = set(cats)
    else:
        cats = []
    missing_cats = set(models.perf_cat.objects.all().exclude(id__in={1}).values_list('name', flat=True))
    perf_forms = models.perf_forms.objects.all().order_by('perf_cat', 'uploaded_at')
    form = forms.perf_forms_submit()
    context = {'perf_forms': perf_forms,
                'form': form,
                'missing_cats':missing_cats,
                'system_access':system_access,}
    return render(request, 'performance/add_perf_forms.html', context)

# Admin function to update employee performance requirements
def add_perf_cats(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    if request.user.username != "system_admin" and not all_user.exists() and not perf_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.add_edit_perf_cats(request.POST)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect(reverse('add_perf_cats'))
    perf_cat = models.perf_cat.objects.all().order_by('name')
    add_edit_perf_cats = forms.add_edit_perf_cats()
    context = {'perf_cat': perf_cat,
                'add_edit_perf_cats': add_edit_perf_cats,
                'system_access':system_access,}
    return render(request, 'performance/add_perf_cats.html', context)

# Admin form to edit the name of the performance categories
@transaction.atomic
def update_perf_cat(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    if request.user.username != "system_admin" and not all_user.exists() and not perf_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        perf_form = models.perf_cat.objects.get(id=pk)
        info_form = forms.add_edit_perf_cats(request.POST, instance=perf_form)
        if info_form.is_valid():
            info_form.save()
            messages.success(request, 'The form was successfully updated!')
            return HttpResponseRedirect(reverse('add_perf_cats'))
        else:
            messages.error(request, 'Please correct the error below.')
            return HttpResponseRedirect(reverse('add_perf_cats'))
    else:
        perf_form = models.perf_cat.objects.get(id=pk)
        info_form = forms.add_edit_perf_cats(instance=perf_form)
        context = {'info_form': info_form,
                    'system_access':system_access,
                   }
    return render(request, 'performance/update_perf_cat.html', context)

# Admin function to view outstanding performance reviews
def outstanding_perf_forms(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    if request.user.username != "system_admin" and not all_user.exists() and not perf_user.exists():
        return HttpResponseRedirect(reverse('home'))
    year = datetime.date.today().year
    month = datetime.date.today().month
    if month < 11:
        year = year - 1
    last_uploaded = models.emp_perf_forms.objects.all().filter(~Q(employee__perf_cat=None), year=year) \
        .values_list('employee_id', flat=True)
    if last_uploaded.exists():
        last_uploaded = set(last_uploaded)
    else:
        last_uploaded = []
    employees_missing = models.Profile.objects.all().exclude(perf_cat=None) \
        .exclude(id__in=last_uploaded) \
        .values('user__first_name', 'user__last_name') \
        .order_by('user__first_name', 'user__last_name')
    manager_missing = models.emp_perf_forms.objects.all() \
        .filter(manager_upload_name=None) \
        .values('employee__manager__user__first_name', 'employee__manager__user__last_name',
            'employee__user__first_name', 'employee__user__last_name',
            'upload', 'upload_name', 'uploaded_at') \
        .order_by('employee__manager__user__first_name', 'employee__manager__user__last_name')
    if 'manager_missing' in request.POST:
        manager_df = pd.DataFrame(list(manager_missing))
        if len(manager_df) < 1:
            manager_df = pd.DataFrame(columns=['employee__manager__user__first_name', 
                'employee__manager__user__last_name', 'employee__user__first_name', 
                'employee__user__last_name', 'upload', 'upload_name', 'uploaded_at'])
        manager_df['employee_name'] = manager_df['employee__user__first_name'] + \
                ' ' + manager_df['employee__user__last_name']
        manager_df['employee_performance_review'] = 'https://blt-construction.s3.amazonaws.com/' + \
                manager_df['upload']
        manager_df['manager_name'] = manager_df['employee__manager__user__first_name'] + \
                ' ' + manager_df['employee__manager__user__last_name']
        manager_df['uploaded_at'] = manager_df['uploaded_at'].dt.date
        manager_df = manager_df[['employee_name', 'employee_performance_review', 'uploaded_at', 
                'manager_name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=performance_reviews_missing_manager_review.csv'
        manager_df.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    if 'employees_missing' in request.POST:
        employees_df = pd.DataFrame(list(employees_missing))
        if len(employees_df.index) < 1:
            employees_df = pd.DataFrame(columns=['user__first_name', 'user__last_name'])
        employees_df['employee_name'] = employees_df['user__first_name'] + \
                ' ' + employees_df['user__last_name']
        employees_df = employees_df[['employee_name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=employees_missing_performance_reviews.csv'
        employees_df.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    context = {
        'employees_missing': employees_missing,
        'year': year,
        'manager_missing':manager_missing,
        'system_access':system_access,
    }
    return render(request, 'performance/outstanding_perf_forms.html', context)

# Admin function to view historical performance reviews
def view_perf_history(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    if request.user.username != "system_admin" and not all_user.exists() and not perf_user.exists():
        return HttpResponseRedirect(reverse('home'))
    completed_perfs = models.emp_perf_forms.objects.all() \
        .exclude(manager_upload_name=None) \
        .values('employee__manager__user__first_name', 'employee__manager__user__last_name',
            'employee__user__first_name', 'employee__user__last_name',
            'upload', 'upload_name', 'uploaded_at', 'year',
            'manager_upload', 'manager_upload_name', 'manager_uploaded_at') \
        .order_by('year', 'employee__user__first_name', 'employee__user__last_name')
    if 'export_all' in request.POST:
        completed_df = pd.DataFrame(list(completed_perfs))
        if len(completed_df.index) < 1:
            completed_df = pd.DataFrame(columns=['employee__manager__user__first_name', 'employee__manager__user__last_name',
            'employee__user__first_name', 'employee__user__last_name',
            'upload', 'upload_name', 'uploaded_at', 'year',
            'manager_upload', 'manager_upload_name', 'manager_uploaded_at'])
        completed_df['employee_name'] = completed_df['employee__user__first_name'] + ' ' + \
                completed_df['employee__user__last_name']
        completed_df['employee_review'] = 'https://blt-construction.s3.amazonaws.com/' + \
                completed_df['upload']
        completed_df['uploaded_at'] = completed_df['uploaded_at'].dt.date
        completed_df['manager_uploaded_at'] = completed_df['manager_uploaded_at'].dt.date
        completed_df['manager_name'] = completed_df['employee__manager__user__first_name'] + ' ' + \
                completed_df['employee__manager__user__last_name']
        completed_df['manager_review'] = 'https://blt-construction.s3.amazonaws.com/' + \
                completed_df['manager_upload']
        completed_df = completed_df[['year', 'employee_name', 'employee_review', 'uploaded_at', 
                'manager_name', 'manager_review', 'manager_uploaded_at']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=performance_reviews.csv'
        completed_df.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    context = {'completed_perfs': completed_perfs,
                'system_access':system_access,
    }
    return render(request, 'performance/view_perf_history.html', context)

def manager_perf_review(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    if request.user.username != "system_admin" and not all_user.exists() and not perf_user.exists():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        manager_obj = models.emp_perf_forms.objects.get(id=pk)
        manager_form = forms.manager_submit_perf(request.POST, request.FILES, instance=manager_obj)
        print(manager_form.errors)
        if manager_form.is_valid():
            obj = manager_form.save(commit=False)
            print("valid")
            obj.manager_uploaded_at = datetime.date.today()
            print(obj.manager_uploaded_at)
            obj.save()
            messages.success(request, 'The form was successfully uploaded!')
            return HttpResponseRedirect(reverse('manager_perf_centre'))
    manager_obj = models.emp_perf_forms.objects.get(id=pk)
    manager_form = forms.manager_submit_perf(instance=manager_obj)
    context = {'manager_form':manager_form,
                'system_access':system_access,
    }
    return render(request, 'performance/manager_perf_review.html', context)

def manager_perf_centre(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    system_access = True
    system_user = models.Profile.objects.all().filter(user_id=user_id)
    if request.user.username != "system_admin" and not system_user.exists():
        system_access = False
    all_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='All')
    perf_user = models.Profile.objects.all().filter(user_id=user_id, access__access_level='Performance')
    if request.user.username != "system_admin" and not all_user.exists() and not perf_user.exists():
        return HttpResponseRedirect(reverse('home'))
    manager = request.user.id
    print(manager)
    completed_perfs = models.emp_perf_forms.objects.all() \
        .filter(employee__manager_id=manager) \
        .exclude(manager_upload_name=None) \
        .values('employee__manager__user__first_name', 'employee__manager__user__last_name',
            'employee__user__first_name', 'employee__user__last_name',
            'upload', 'upload_name', 'uploaded_at', 'year',
            'manager_upload', 'manager_upload_name', 'manager_uploaded_at') \
        .order_by('year', 'employee__user__first_name', 'employee__user__last_name')
    outstanding_perfs = models.emp_perf_forms.objects.all() \
        .filter(employee__manager_id=manager, manager_upload_name=None) \
        .values('employee__manager__user__first_name', 'employee__manager__user__last_name',
            'employee__user__first_name', 'employee__user__last_name',
            'upload', 'upload_name', 'uploaded_at', 'year',
            'manager_upload', 'manager_upload_name', 'manager_uploaded_at') \
        .order_by('year', 'employee__user__first_name', 'employee__user__last_name')
    emp_list = models.Profile.objects.all() \
        .filter(manager_id=manager) \
        .values('user__first_name', 'user__last_name')
    context = {'completed_perfs':completed_perfs,
                'outstanding_perfs':outstanding_perfs,
                'emp_list':emp_list,
                'system_access':system_access,
    }
    return render(request, 'performance/manager_perf_centre.html', context)


