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

# Employee function to view performance reviews
def performance_reviews(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    return render(request, 'performance/performance_reviews.html')

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
    perf_forms = models.perf_forms.objects.all().order_by('perf_cat', 'uploaded_at')
    form = forms.perf_forms_submit()
    context = {'perf_forms': perf_forms,
                'form': form,}
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
    return render(request, 'performance/outstanding_perf_forms.html')

# Admin function to view historical performance reviews
def view_perf_history(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'performance/view_perf_history.html')