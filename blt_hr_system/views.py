from django.urls import reverse
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from . import models
from . import forms
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

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')

def account(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    return render(request, 'account.html')

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
    return render(request, 'review_cert_requests.html', context)

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
                message = render_to_string('cert_approved.html', {
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
                message = render_to_string('cert_rejected.html', {
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
    return render(request, 'review_cert.html',context)

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
    return render(request, 'certifications_maintained.html',context)

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
            return HttpResponseRedirect(reverse('certifications'))
    else:
        cert = models.certification.objects.get(id=pk)
        certs_form = forms.add_certification(instance=cert)
        context = {'certs_form': certs_form,}
    return render(request, 'edit_system_certs.html', context)

def employee_required_certs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'employee_required_certs.html', context)

def add_birth_date(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        birth_date = forms.add_birth_date(request.POST, instance=request.user.profile)
        if birth_date.is_valid():
            birth_date.save()
            messages.success(request, 'Your birth dates was successfully updated!')
            return HttpResponseRedirect(reverse('account'))
    else:
        birth_date = forms.add_birth_date(instance=request.user.profile)
        context = {'birth_date':birth_date}
    return render(request, 'add_birth_date.html', context)

def managed_certs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        cert_form = forms.add_certification(request.POST)
        cert_form.save()
        return HttpResponseRedirect(reverse('certifications'))
    else:
        cert_form = forms.add_certification()
        cert_info = models.certification.objects.all()
        context = {'cert_form': cert_form,
                   'cert_info' : cert_info}
    return render(request, 'managed_certs.html', context)

def manage_onboarding_docs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        doc_form = forms.add_onboarding_doc(request.POST)
        if doc_form.is_valid():
            doc_form.save()
            return HttpResponseRedirect(reverse('manage_onboarding_docs'))
        else:
            error_msg = True
            print(request.POST.get('doc'))
            document_inst = models.training_docs.objects.get(id=request.POST.get('doc'))
            document_name = document_inst.upload_name
            doc_form = forms.add_onboarding_doc()
            doc_info = models.onboarding_docs.objects.all()
            context = {'doc_form': doc_form,
                       'doc_info' : doc_info,
                       'error_msg':error_msg,
                       'document_name':document_name,
            }
            return render(request, 'manage_onboarding_docs.html', context)
    else:
        doc_form = forms.add_onboarding_doc()
        doc_info = models.onboarding_docs.objects.all()
        error_msg = False
        context = {'doc_form': doc_form,
                   'doc_info' : doc_info,
                   'error_msg':error_msg,}
    return render(request, 'manage_onboarding_docs.html', context)

def edit_onboarding_docs(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        doc = models.onboarding_docs.objects.get(id=pk)
        doc_form = forms.add_onboarding_doc(request.POST, instance=doc)
        if doc_form.is_valid():
            doc_form.save()
            messages.success(request, 'The certification was successfully updated!')
            return HttpResponseRedirect(reverse('manage_onboarding_docs'))
        else:
            error_msg = True
            print(request.POST.get('doc'))
            document_inst = models.training_docs.objects.get(id=request.POST.get('doc'))
            document_name = document_inst.upload_name
            doc = models.onboarding_docs.objects.get(id=pk)
            doc_form = forms.add_onboarding_doc(instance=doc)
            doc_info = models.onboarding_docs.objects.all()
            context = {'doc_form': doc_form,
                       'doc_info' : doc_info,
                       'error_msg':error_msg,
                       'document_name':document_name,
            }
            return render(request, 'edit_onboarding_docs.html', context)
    else:
        doc = models.onboarding_docs.objects.get(id=pk)
        doc_form = forms.add_onboarding_doc(instance=doc)
        context = {'doc_form': doc_form,}
        return render(request, 'edit_onboarding_docs.html', context)

def certifications(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    cert_info = models.certification.objects.all().order_by('name')
    context = {'cert_info' : cert_info}
    return render(request, 'certifications.html', context)

@transaction.atomic
def update_profile(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        user_account = User.objects.get(id=pk)
        user_form = forms.UserForm(request.POST, instance=user_account)
        profile_form = forms.ProfileForm(request.POST, instance=user_account.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'The employee profile was successfully updated!')
            return HttpResponseRedirect(reverse('employee_directory_edit'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_account = User.objects.get(id=pk)
        user_form = forms.UserForm(instance=user_account)
        profile_form = forms.ProfileForm(instance=user_account.profile)
    return render(request, 'edit_employee_info.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

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
        return render(request, 'edit_required_certs.html', context)

def employee_directory(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    users = User.objects.all().filter(is_active=True).exclude(username='system_admin').order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'employee_directory.html', context)

def company_locations(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    locations = models.company_info.objects.all().order_by('location')
    context = {'locations' : locations}
    return render(request, 'company_locations.html', context)

def employee_directory_edit(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.username != "system_admin":
        return redirect('home')
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'employee_directory_edit.html', context)

def signup(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            # submit employee informatation to create an account with profile information
            obj = form.save()
            obj.refresh_from_db() 
            obj.profile.start_date = request.POST['start_date']
            profile_instance = models.Profile.objects.get(pk=request.POST['manager'])
            obj.profile.manager = profile_instance
            location_instance = models.company_info.objects.get(pk=request.POST['location'])
            obj.profile.location = location_instance
            obj.profile.position = request.POST['position']
            obj.profile.certs.set(request.POST.getlist('certifications'))
            obj.profile.save()
            # send an email to the user to let them know that their account has been setup
            password = request.POST['password1']
            username = request.POST['username']
            domain = request.META['HTTP_HOST']
            mail_subject = 'Welcome to your BLT HR System.'
            message = render_to_string('acc_active_email.html', {
                'username': username,
                'password': password,
                'domain': domain,
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponseRedirect(reverse('employee_directory_edit'))
    else:
        form = forms.SignUpForm()
    return render(request, 'signup.html', {'form': form})

def delete_training_doc(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.training_docs_submit(request.POST)
        documents = models.training_docs.objects.all()
        id_val = request.POST.get('document_name')
        onboard_doc = list(models.onboarding_docs.objects.filter(doc=id_val).all().values_list('name'))
        if len(onboard_doc) == 0:
            item = models.training_docs.objects.get(id=id_val)
            item.delete()
            return HttpResponseRedirect(reverse('training_center'))
        else:
            form = forms.remove_doc()
            message = True
            invalid_doc = models.onboarding_docs.objects.filter(doc=id_val).all()
            document_inst = models.training_docs.objects.get(id=id_val)
            document_name = document_inst.upload_name
            context = {'document_name': document_name, 
                        'documents': documents,
                        'form': form,
                        'message': message,
                        'invalid_doc': invalid_doc,}
            return render(request, 'delete_training_doc.html', context) 
    form = forms.remove_doc()
    documents = models.training_docs.objects.all()
    message = False
    context = {'documents': documents,
                'form': form,
                'message': message,}
    return render(request, 'delete_training_doc.html', context)    

def training_material(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.training_docs_submit(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.uploaded_by = request.user
            obj.save()
            if request.POST.get('onbard_doc'):
                # update the onboarding / training doc to point to this new document
                onbaord_inst = models.onboarding_docs.objects.get(id=request.POST.get('onbard_doc'))
                onbaord_inst.doc = obj
                onbaord_inst.save()
                if request.POST.get('update_read'):
                    # assign all values of 'update_read' to False where doc_read_req.doc == onbaord_inst.id
                    update_read_mod = models.doc_read_req.objects.all().filter(doc=onbaord_inst.id)
                    for inst in update_read_mod:
                        inst.read = False
                if request.POST.get('update_submit'):
                    # assign all values of 'update_submit' to False where doc_submit_req.doc == onbaord_inst.id
                    update_submit_mod = models.doc_submit_req.objects.all().filter(doc=onbaord_inst.id)
                    for inst in update_submit_mod:
                        inst.submitted = False
            return HttpResponseRedirect(reverse('training_center'))
    documents = models.training_docs.objects.all()
    form = forms.training_docs_submit()
    context = {'documents': documents,
                'form': form,}
    return render(request, 'training_material.html', context)

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
        return HttpResponseRedirect(reverse('certifications_maintained'))
    cert_request = forms.cert_request()
    context = {'cert_request': cert_request}
    return render(request, 'certification_request.html', context)

def absence_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('home'))
    else:
        absence_form = forms.absence_request()
    context = {'absence_form': absence_form}
    return render(request, 'absence_request.html', context)

def add_company_info(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        company_info_form = forms.submit_company_info(request.POST)
        company_info_form.save()
        return HttpResponseRedirect(reverse('company_locations'))
    else:
        company_info_form = forms.submit_company_info()
        company_info = models.company_info.objects.all()
        context = {'company_info_form': company_info_form,
                   'company_info' : company_info}
        return render(request, 'add_company_info.html', context)

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
        return render(request, 'edit_company_info.html', context)

def training_center(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    documents = models.training_docs.objects.all()
    documents = documents.order_by('upload_name')
    context = {'documents': documents,}
    return render(request, 'training_center.html', context)

def performance_reviews(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    return render(request, 'performance_reviews.html')

def admin(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'admin.html')

def acknowledge_requirement(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    sql = """
        SELECT "auth_user"."id", 
               "auth_user"."first_name", 
                "auth_user"."last_name", 
                array_agg("blt_hr_system_onboarding_docs"."name") AS doc
        FROM "auth_user" 
        LEFT JOIN "blt_hr_system_doc_read_req" 
            on "auth_user"."id" = "blt_hr_system_doc_read_req"."employee_id"
        LEFT JOIN "blt_hr_system_onboarding_docs"
            on "blt_hr_system_doc_read_req"."doc_id" = "blt_hr_system_onboarding_docs"."id"
        GROUP BY "auth_user"."id", 
                 "auth_user"."first_name", 
                 "auth_user"."last_name"
        ORDER BY "auth_user"."first_name", 
                 "auth_user"."last_name"
         """
    cursor = connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    print(data)
    context = {'data':data
    }
    return render(request, 'acknowledge_requirement.html', context)

@transaction.atomic
def edit_ack_requirement(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        doc_req = models.doc_read_req.objects.all().filter(employee=pk)
        user_mod = User.objects.get(id=pk)
        for u in doc_req:
            u.delete()
        for i in request.POST.getlist('docs'):
            onboard_doc = models.onboarding_docs.objects.get(id=i)
            models.doc_read_req.objects.create(employee=user_mod, doc=onboard_doc, read=False)
        return HttpResponseRedirect(reverse('acknowledge_requirement'))
    doc_req = models.doc_read_req.objects.all().filter(employee=pk)
    name = User.objects.get(id=pk)
    name_print = name.first_name + ' ' + name.last_name
    edit_ack_require = forms.edit_ack_require(pk=pk)
    context = {'name_print': name_print,
                'edit_ack_require': edit_ack_require}
    return render(request, 'edit_ack_requirement.html', context)

def submission_required(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    context = {

    }
    return render(request, 'submission_required.html', context)
