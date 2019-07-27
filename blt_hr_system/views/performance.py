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
    user = request.user.id
    perf_type = models.Profile.objects.values_list('perf_cat', flat=True).get(id=user)
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
    form = forms.submit_perf()
    context = {'req_perf':req_perf,
                'perf_required':perf_required,
                'completed_forms':completed_forms,
                'form':form,
                'upload_req':upload_req,
                'year':year,
    }
    return render(request, 'performance/performance_reviews.html', context)

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------
def add_edit_perf_cat(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    perf_cat = models.Profile.objects.all().order_by('user__first_name', 'user__last_name')
    context = {'perf_cat': perf_cat,}
    return render(request, 'performance/add_edit_perf_cat.html', context)

def edit_emp_perf_cat(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
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
                   'perf_form': perf_form,}
    return render(request, 'performance/edit_emp_perf_cat.html', context)

# Admin function to add, view and edit performance review forms
def add_perf_forms(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
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
                'missing_cats':missing_cats,}
    return render(request, 'performance/add_perf_forms.html', context)

# Admin function to update employee performance requirements
def add_perf_cats(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.add_edit_perf_cats(request.POST)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect(reverse('add_perf_cats'))
    perf_cat = models.perf_cat.objects.all().order_by('name')
    add_edit_perf_cats = forms.add_edit_perf_cats()
    context = {'perf_cat': perf_cat,
                'add_edit_perf_cats': add_edit_perf_cats,}
    return render(request, 'performance/add_perf_cats.html', context)

# Admin form to edit the name of the performance categories
@transaction.atomic
def update_perf_cat(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
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
                   }
    return render(request, 'performance/update_perf_cat.html', context)

# Admin function to view outstanding performance reviews
def outstanding_perf_forms(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
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
    print(last_uploaded)
    employees_missing = models.Profile.objects.all().exclude(perf_cat=None).exclude(id__in=last_uploaded)
    context = {
        'employees_missing': employees_missing,
        'year': year,
    }
    return render(request, 'performance/outstanding_perf_forms.html', context)

# Admin function to view historical performance reviews
def view_perf_history(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'performance/view_perf_history.html')