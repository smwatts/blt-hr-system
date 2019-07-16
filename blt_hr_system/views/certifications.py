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

# General function that shows the system managed certifications
def certs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    cert_info = models.certification.objects.all().order_by('name')
    context = {'cert_info' : cert_info}
    return render(request, 'certifications/certs.html', context)

# ------------------------------------------------------------------
# EMPLOYEE FUNCTIONS
# ------------------------------------------------------------------

# Employee function to view all personal certifications
def certifications_maintained(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    now = datetime.datetime.now()
    day_30 = datetime.datetime.now() + datetime.timedelta(days=30)
    pending_certs = models.employee_certification.objects.all().filter(employee_id=request.user.id, is_approved=False)
    curr_certs = models.employee_certification.objects.all().filter(employee_id=request.user.id, 
        is_approved=True, exp_date__gte=now)
    curr_certs_flat = list(curr_certs.values_list('cert_name', flat=True))
    exp_certs = models.employee_certification.objects.all().filter(employee_id=request.user.id, 
        is_approved=True, exp_date__lte=day_30)
    exp_certs_flat = list(exp_certs.values_list('cert_name', flat=True))
    all_certs = models.Profile.objects.all().filter(user_id=request.user.id)
    all_certs_flat = list(all_certs.values_list('certs', flat=True))
    remain_certs = list(all_certs.filter(certs__in=[x for x in all_certs_flat if x not in curr_certs_flat 
        and x not in exp_certs_flat]).distinct().values_list('certs', flat=True))
    missing_certs = models.certification.objects.filter(id__in=remain_certs)
    no_expire = datetime.datetime.strptime('3000-01-01', '%Y-%m-%d')
    context = {'pending_certs':pending_certs,
               'curr_certs':curr_certs,
               'exp_certs':exp_certs,
               'missing_certs':missing_certs,
               'no_expire':no_expire,
    }
    return render(request, 'certifications/certifications_maintained.html',context)

# Employee function for employees to submit a certification
def certification_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        form = forms.cert_request(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.employee_id = request.user
            obj.is_approved = False
            cert = models.certification.objects.filter(pk=request.POST['cert_name'])
            for c in cert:
                exp_yrs = c.expiration_yrs
            if exp_yrs == 0:
                obj.exp_date = datetime.datetime.strptime('3000-01-01', '%Y-%m-%d')
            else:
                obj.exp_date = datetime.datetime.strptime(request.POST['acq_date'], '%Y-%m-%d') + datedelta.datedelta(years=exp_yrs)
            obj.save()
        return HttpResponseRedirect(reverse('certs'))
    cert_request = forms.cert_request()
    context = {'cert_request': cert_request}
    return render(request, 'certifications/certification_request.html', context)

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------

# Admin function to add certifications
def managed_certs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        cert_form = forms.add_certification(request.POST)
        cert_form.save()
        return HttpResponseRedirect(reverse('managed_certs'))
    else:
        cert_form = forms.add_certification()
        cert_info = models.certification.objects.all()
        context = {'cert_form': cert_form,
                   'cert_info' : cert_info}
    return render(request, 'certifications/managed_certs.html', context)

# Admin function to view all certification requests ready for review
def review_cert_requests(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    pending_approval = models.employee_certification.objects.all().filter(is_approved=False)
    no_expire = datetime.datetime.strptime('3000-01-01', '%Y-%m-%d')
    context = {'pending_approval':pending_approval,
               'no_expire':no_expire,
    }
    return render(request, 'certifications/review_cert_requests.html', context)

# Admin function to review individual certification requests
def review_cert(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        cert = models.employee_certification.objects.get(id=pk)
        review_cert = forms.review_cert(request.POST, instance=cert)
        user_info = User.objects.get(id=request.POST.get('employee_id'))
        user_email = user_info.email
        cert_info = models.certification.objects.get(id=request.POST.get('cert_name'))
        cert_name = cert_info.name
        if review_cert.is_valid():
            if request.POST.get('is_approved'):
                review_cert.save()
                replace_certs = models.employee_certification.objects.filter(cert_name=
                    request.POST.get('cert_name'), employee_id=
                    request.POST.get('employee_id')).exclude(id=pk)
                for replace in replace_certs:
                    replace.delete()
                messages.success(request, 'The certification was successfully approved!')
                # send a message to the recipient telling them their certification was approved!
                domain = request.META['HTTP_HOST']
                mail_subject = 'Certification review results: ' + cert_name
                message = render_to_string('certifications/cert_approved.html', {
                    'cert_name': cert_name,
                    'message': request.POST.get('message'),
                    'domain': domain,
                })
                to_email = user_email
                email = EmailMessage(
                            mail_subject, message, to=[to_email]
                )
                email.send()
                return HttpResponseRedirect(reverse('review_cert_requests'))
            else:   
                cert.delete()
                messages.success(request, 'The certification was successfully rejected.')
                # send a message to the recipient telling them their certification was approved!
                domain = request.META['HTTP_HOST']
                mail_subject = 'Certification review results: ' + cert_name
                message = render_to_string('certifications/cert_rejected.html', {
                    'cert_name': cert_name,
                    'message': request.POST.get('message'),
                    'domain': domain,
                })
                to_email = user_email
                email = EmailMessage(
                            mail_subject, message, to=[to_email]
                )
                email.send()
        return HttpResponseRedirect(reverse('review_cert_requests'))
    cert = models.employee_certification.objects.get(id=pk)
    review_cert = forms.review_cert(instance=cert)
    no_expire = datetime.datetime.strptime('3000-01-01', '%Y-%m-%d')
    context = {'cert':cert,
               'review_cert':review_cert,
               'no_expire':no_expire,
    }
    return render(request, 'certifications/review_cert.html',context)

# Admin function to view all certifications required for each employee
def employee_required_certs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'certifications/employee_required_certs.html', context)

# Admin function to edit individual system managed certifications
def edit_system_certs(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        cert = models.certification.objects.get(id=pk)
        certs_form = forms.add_certification(request.POST, instance=cert)
        if certs_form.is_valid():
            update_certs = models.employee_certification.objects.filter(cert_name=pk)
            for update in update_certs:
                if int(request.POST['expiration_yrs']) == 0:
                    update.exp_date = datetime.datetime.strptime('3000-01-01', '%Y-%m-%d')
                    update.save()
                else:
                    update.exp_date = update.acq_date + datedelta.datedelta(years=int(request.POST['expiration_yrs']))
                    update.save()
            certs_form.save()
            messages.success(request, 'The certification was successfully updated!')
            return HttpResponseRedirect(reverse('managed_certs'))
    else:
        cert = models.certification.objects.get(id=pk)
        certs_form = forms.add_certification(instance=cert)
        context = {'certs_form': certs_form,}
    return render(request, 'certifications/edit_system_certs.html', context)

# Admin function to edit certification requirements for individual employees
@transaction.atomic
def edit_required_certs(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        user_account = User.objects.get(id=pk)
        certs_form = forms.edit_system_certs(request.POST, instance=user_account.profile)
        user_account.profile.certs.set(request.POST.getlist('certs'))
        messages.success(request, 'The employee certifications were successfully updated!')
        return HttpResponseRedirect(reverse('employee_required_certs'))
    else:
        user_account = User.objects.get(id=pk)
        certs_form = forms.edit_system_certs(instance=user_account.profile)
        context = {'user_account': user_account,
                    'certs_form': certs_form,}
        return render(request, 'certifications/edit_required_certs.html', context)
