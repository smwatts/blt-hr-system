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

# -----------------------------------------------------------------
# GENERAL/HELPER FUNCTIONS
# -----------------------------------------------------------------

# Lists all the training documents
# TO DO: Display only active documents
def training_center(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    documents = models.training_docs.objects.all()
    documents = documents.order_by('upload_name')
    context = {'documents': documents,}
    return render(request, 'training_docs/training_center.html', context)

# ------------------------------------------------------------------
# EMPLOYEE FUNCTIONS
# ------------------------------------------------------------------

# Employee function to dispaly all onboarding requirements for an employee
def onboarding_training_docs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    current_user = request.user.id
    df_ack = combine_ack_datasets('outstanding', current_user)
    dic_ack = df_ack.T.to_dict().values()
    df_sub = combine_sub_datasets('outstanding', current_user)
    if 'export_ack' in request.POST:
        df_ack['employee__name'] = df_ack['employee__first_name'] + ' ' + df_ack['employee__last_name']
        df_ack['doc__url'] = 'https://blt-construction.s3.amazonaws.com/' + df_ack['doc__url']
        df_ack_exp = df_ack[['employee__name', 'doc__name', 'doc__url', 'onboarding_cat__name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=completed_document_acknowledgements.csv'
        df_ack_exp.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    if 'export_sub' in request.POST:
        df_sub['employee__name'] = df_sub['employee__first_name'] + ' ' + df_sub['employee__last_name']
        df_sub['doc__url'] = 'https://blt-construction.s3.amazonaws.com/' + df_sub['doc__url']
        df_sub_exp = df_sub[['employee__name', 'doc__name', 'doc__url', 'onboarding_cat__name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=completed_document_submissions.csv'
        df_sub_exp.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    dic_sub = df_sub.T.to_dict().values()
    context = {'dic_ack': dic_ack,
               'dic_sub': dic_sub,
    }
    return render(request, 'training_docs/onboarding_training_docs.html', context) 

# Employee function to acknowledge when a form has been read
def ack_doc_read(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id
    if request.method == 'POST':
        row = models.doc_read.objects.create(employee_id=user_id, doc_id=pk)
        return HttpResponseRedirect(reverse('onboarding_training_docs'))
    employee = User.objects.get(id=user_id)
    doc = models.training_docs.objects.get(id=pk)
    context = {'employee': employee,
               'doc': doc,
    }
    return render(request, 'training_docs/ack_doc_read.html', context) 

# Employee function to view & export all 
def completed_ack_sub_docs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_id = request.user.id  
    df_ack = combine_ack_datasets('obtained', user_id)
    dic_ack = df_ack.T.to_dict().values()
    df_sub = combine_sub_datasets('obtained', user_id)
    dic_sub = df_sub.T.to_dict().values()
    if 'export_ack' in request.POST:
        df_ack['employee__name'] = df_ack['employee__first_name'] + ' ' + df_ack['employee__last_name']
        df_ack['doc__url'] = 'https://blt-construction.s3.amazonaws.com/' + df_ack['doc__url']
        df_ack_exp = df_ack[['employee__name', 'doc__name', 'doc__url', 'onboarding_cat__name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=completed_document_acknowledgements.csv'
        df_ack_exp.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    if 'export_sub' in request.POST:
        df_sub['employee__name'] = df_sub['employee__first_name'] + ' ' + df_sub['employee__last_name']
        df_sub['doc__url'] = 'https://blt-construction.s3.amazonaws.com/' + df_sub['doc__url']
        df_sub_exp = df_sub[['employee__name', 'doc__name', 'doc__url', 'onboarding_cat__name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=completed_document_submissions.csv'
        df_sub_exp.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    context = {'dic_ack': dic_ack,
               'dic_sub': dic_sub,
    }  
    return render(request, 'training_docs/completed_ack_sub_docs.html', context)

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------

# Admin function to add a new training documents
# If the doc is an "onboarding" doc then it must be "re-ack"/"re-submit"
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
            onboarding_cat = obj.onboarding_cat
            pk = obj.id
            onboard_doc = models.training_docs.objects.filter(~Q(id=pk), onboarding_cat=onboarding_cat)
            return HttpResponseRedirect(reverse('training_material'))
    documents = models.training_docs.objects.all().order_by('upload_name')
    form = forms.training_docs_submit()
    context = {'documents': documents,
                'form': form,}
    return render(request, 'training_docs/training_material.html', context)

# Admin function to remove documents from the system
# TO DO: change the functionality to "active/inactive" instead of removing docs
def delete_training_doc(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    documents = models.training_docs.objects.all()
    context = {'documents': documents,}
    return render(request, 'training_docs/delete_training_doc.html', context)  

# Admin function to delete documents from the system
def change_doc_status(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        doc = models.training_docs.objects.get(id=pk)
        doc_form = forms.remove_doc(request.POST, instance=doc)
        if doc_form.is_valid():
            if 'delete_document' in request.POST:
                doc.delete()
            messages.success(request, 'The training document was successfully deleted!')
            return HttpResponseRedirect(reverse('delete_training_doc'))
    doc = models.training_docs.objects.get(id=pk)
    form = forms.remove_doc(instance=doc)
    context = {'form': form, 'doc':doc}
    return render(request, 'training_docs/change_doc_status.html', context)

# Admin function to create onboarding form categories
def manage_onboarding_docs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        doc_form = forms.add_onboarding_cat(request.POST)
        if doc_form.is_valid():
            doc_form.save()
            return HttpResponseRedirect(reverse('manage_onboarding_docs'))
    else:
        doc_form = forms.add_onboarding_cat()
        doc_info = models.onboarding_cat.objects.all()
        context = {'doc_form': doc_form,
                   'doc_info' : doc_info,}
    return render(request, 'training_docs/manage_onboarding_docs.html', context)

# Admin function to edit an onboarding category
# TO DO: Figure out what "editting an onboarding category" means
#        Can we remove docs from that category? What happens when we do?
def edit_onboarding_cat(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        doc = models.onboarding_cat.objects.get(id=pk)
        doc_form = forms.add_onboarding_cat(request.POST, instance=doc)
        if doc_form.is_valid():
            doc_form.save()
            messages.success(request, 'The onboarding category was successfully updated!')
            return HttpResponseRedirect(reverse('manage_onboarding_docs'))
    else:
        doc = models.onboarding_cat.objects.get(id=pk)
        doc_form = forms.add_onboarding_cat(instance=doc)
        context = {'doc_form': doc_form,}
        return render(request, 'training_docs/edit_onboarding_cat.html', context)

# Admin function to display the onboarding "ack" & "submit" requirements for all employees
def onboarding_requirement(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {'users' : users}
    return render(request, 'training_docs/onboarding_requirement.html', context)

# Admin function to change the onboarding document "ack" requirement for
# an individual employee
@transaction.atomic
def edit_ack_requirement(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        user_account = User.objects.get(id=pk)
        ack_form = forms.edit_ack_require(request.POST, instance=user_account.profile)
        user_account.profile.read_req.set(request.POST.getlist('read_req'))
        messages.success(request, 'The employee acknolwedgement requirement was successfully updated!')
        return HttpResponseRedirect(reverse('onboarding_requirement'))
    else:
        user_account = User.objects.get(id=pk)
        ack_form = forms.edit_ack_require(instance=user_account.profile)
        context = {'user_account': user_account,
                    'ack_form': ack_form,}
    return render(request, 'training_docs/edit_ack_requirement.html', context)

# Admin function to change the onboarding document "submit" requirement for
# an individual employee
@transaction.atomic
def edit_submission_req(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        user_account = User.objects.get(id=pk)
        sub_form = forms.edit_sub_require(request.POST, instance=user_account.profile)
        user_account.profile.submit_req.set(request.POST.getlist('submit_req'))
        messages.success(request, 'The employee acknolwedgement requirement was successfully updated!')
        return HttpResponseRedirect(reverse('onboarding_requirement'))
    else:
        user_account = User.objects.get(id=pk)
        sub_form = forms.edit_sub_require(instance=user_account.profile)
        context = {'user_account': user_account,
                    'sub_form': sub_form,}
    return render(request, 'training_docs/edit_doc_submission.html', context)

# Admin function to review each employee and the status of their "submitted" onboarding documents 
# This view will the display submitted & outstanding forms for each employee
def review_sub_docs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    df_ack = combine_ack_datasets('obtained', 'all')
    dic_ack = df_ack.T.to_dict().values()
    df_sub = combine_sub_datasets('obtained', 'all')
    dic_sub = df_sub.T.to_dict().values()
    if 'export_ack' in request.POST:
        df_ack['employee__name'] = df_ack['employee__first_name'] + ' ' + df_ack['employee__last_name']
        df_ack['doc__url'] = 'https://blt-construction.s3.amazonaws.com/' + df_ack['doc__url']
        df_ack_exp = df_ack[['employee__name', 'doc__name', 'doc__url', 'onboarding_cat__name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=completed_document_acknowledgements.csv'
        df_ack_exp.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    if 'export_sub' in request.POST:
        df_sub['employee__name'] = df_sub['employee__first_name'] + ' ' + df_sub['employee__last_name']
        df_sub['doc__url'] = 'https://blt-construction.s3.amazonaws.com/' + df_sub['doc__url']
        df_sub_exp = df_sub[['employee__name', 'doc__name', 'doc__url', 'onboarding_cat__name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=completed_document_submissions.csv'
        df_sub_exp.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    context = {'dic_ack': dic_ack,
               'dic_sub': dic_sub,
    }
    return render(request, 'training_docs/review_sub_docs.html', context)

# Admin function to review missing submissions and acknowledged forms
def review_ack_docs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    df_ack = combine_ack_datasets('outstanding', 'all')
    dic_ack = df_ack.T.to_dict().values()
    df_sub = combine_sub_datasets('outstanding', 'all')
    if 'export_ack' in request.POST:
        df_ack['employee__name'] = df_ack['employee__first_name'] + ' ' + df_ack['employee__last_name']
        df_ack['doc__url'] = 'https://blt-construction.s3.amazonaws.com/' + df_ack['doc__url']
        df_ack_exp = df_ack[['employee__name', 'doc__name', 'doc__url', 'onboarding_cat__name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=completed_document_acknowledgements.csv'
        df_ack_exp.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    if 'export_sub' in request.POST:
        df_sub['employee__name'] = df_sub['employee__first_name'] + ' ' + df_sub['employee__last_name']
        df_sub['doc__url'] = 'https://blt-construction.s3.amazonaws.com/' + df_sub['doc__url']
        df_sub_exp = df_sub[['employee__name', 'doc__name', 'doc__url', 'onboarding_cat__name']]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=completed_document_submissions.csv'
        df_sub_exp.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
        return response
    dic_sub = df_sub.T.to_dict().values()
    context = {'dic_ack': dic_ack,
               'dic_sub': dic_sub,
    }
    return render(request, 'training_docs/review_ack_docs.html', context)

def combine_ack_datasets(type_selected, user_selected):
    # create one dataframe that contains all of the documents a users must acknowledge
    df_req = pd.DataFrame(list(models.Profile.objects.all().values('read_req__name', 'read_req', 'user__first_name', 
        'user__last_name', 'user')))
    if len(df_req.index) < 1:
        df_req = pd.DataFrame(columns=['read_req__name', 'read_req', 'user__first_name', 
        'user__last_name', 'user'])
    df_req = df_req[df_req['read_req__name'].notnull()]
    df_onboard_cats = pd.DataFrame(list(models.training_docs.objects.all().values('onboarding_cat', 
        'onboarding_cat__name', 'upload_name', 'id', 'upload')))
    if len(df_onboard_cats.index) < 1:
        df_onboard_cats = pd.DataFrame(columns=['onboarding_cat', 'onboarding_cat__name', 'upload_name', 'id'])
    df_req = pd.merge(df_req, df_onboard_cats, left_on='read_req', right_on='onboarding_cat')
    df_req = df_req[['user__first_name','user__last_name', 'user', 'onboarding_cat__name', 'onboarding_cat', 
                'upload_name', 'id', 'upload']]
    df_req = df_req.rename(columns={'upload_name': 'doc__name', 'id': 'doc', 'upload' : 'doc__url',
        'user__first_name': 'employee__first_name', 'user__last_name':'employee__last_name', 'user':'employee'})
    # create one dataframe that contains all of the documents that the user has acknowledged
    df_obtained = pd.DataFrame(list(models.doc_read.objects.all().values('employee__first_name', 
        'employee__last_name', 'employee', 'doc__upload_name', 'doc')))
    if len(df_obtained) < 1:
        df_obtained = pd.DataFrame(columns=['employee__first_name', 'employee__last_name', 
            'employee', 'doc__upload_name', 'doc'])
    df_obtained = pd.merge(df_obtained, df_onboard_cats, left_on='doc', right_on='id')
    df_obtained = df_obtained[['employee__first_name', 'employee__last_name', 'employee', 
        'onboarding_cat__name', 'onboarding_cat', 'doc__upload_name', 'doc', 'upload']]
    df_obtained = df_obtained.rename(columns={'doc__upload_name': 'doc__name', 'upload' : 'doc__url'})
    if user_selected != 'all':
        df_obtained = df_obtained.query('employee == @user_selected')
        df_req = df_req.query('employee == @user_selected')
    df_obtained['id'] = df_obtained.employee.map(str) + " - " + df_obtained.doc.map(str)
    df_req['id'] = df_req.employee.map(str) + " - " + df_req.doc.map(str)
    if type_selected == 'obtained':
        df_obtained = df_obtained.sort_values(by=['employee__first_name', 'employee__last_name', 'doc__name'])
        return df_obtained
    else:
        df_list = set(df_obtained['id'])
        df_outstanding = df_req[~df_req['id'].isin(df_list)]
        df_outstanding = df_outstanding.sort_values(by=['employee__first_name', 'employee__last_name', 'doc__name'])
        return df_outstanding

def combine_sub_datasets(type_selected, user_selected):
    # create one dataframe that contains all of the documents a users must acknowledge
    df_req = pd.DataFrame(list(models.Profile.objects.all().values('submit_req__name', 'submit_req', 'user__first_name', 
        'user__last_name', 'user')))
    if len(df_req.index) < 1:
        df_req = pd.DataFrame(columns=['submit_req__name', 'submit_req', 'user__first_name', 
        'user__last_name', 'user'])
    df_req = df_req[df_req['submit_req__name'].notnull()]
    df_onboard_cats = pd.DataFrame(list(models.training_docs.objects.all().values('onboarding_cat', 
        'onboarding_cat__name', 'upload_name', 'id', 'upload')))
    if len(df_onboard_cats.index) < 1:
        df_onboard_cats = pd.DataFrame(columns=['onboarding_cat', 'onboarding_cat__name', 'upload_name', 'id'])
    df_req = pd.merge(df_req, df_onboard_cats, left_on='submit_req', right_on='onboarding_cat')
    df_req = df_req[['user__first_name','user__last_name', 'user', 'onboarding_cat__name', 'onboarding_cat', 
                'upload_name', 'id', 'upload']]
    df_req = df_req.rename(columns={'upload_name': 'doc__name', 'id': 'doc', 'upload' : 'doc__url',
        'user__first_name': 'employee__first_name', 'user__last_name':'employee__last_name', 'user':'employee'})
    # create one dataframe that contains all of the documents that the user has acknowledged
    df_obtained = pd.DataFrame(list(models.doc_submit_req.objects.all().values('employee__first_name', 
        'employee__last_name', 'employee', 'doc__upload_name', 'doc')))
    if len(df_obtained) < 1:
        df_obtained = pd.DataFrame(columns=['employee__first_name', 'employee__last_name', 
            'employee', 'doc__upload_name', 'doc'])
    df_obtained = pd.merge(df_obtained, df_onboard_cats, left_on='doc', right_on='id')
    df_obtained = df_obtained[['employee__first_name', 'employee__last_name', 'employee', 
        'onboarding_cat__name', 'onboarding_cat', 'doc__upload_name', 'doc', 'upload']]
    df_obtained = df_obtained.rename(columns={'doc__upload_name': 'doc__name', 'upload' : 'doc__url'})
    if user_selected != 'all':
        df_obtained = df_obtained.query('employee == @user_selected')
        df_req = df_req.query('employee == @user_selected')
    df_obtained['id'] = df_obtained.employee.map(str) + " - " + df_obtained.doc.map(str)
    df_req['id'] = df_req.employee.map(str) + " - " + df_req.doc.map(str)
    if type_selected == 'obtained':
        df_obtained = df_obtained.sort_values(by=['employee__first_name', 'employee__last_name', 'doc__name'])
        return df_obtained
    else:
        df_list = set(df_obtained['id'])
        df_outstanding = df_req[~df_req['id'].isin(df_list)]
        df_outstanding = df_outstanding.sort_values(by=['employee__first_name', 'employee__last_name', 'doc__name'])
        return df_outstanding

# Admin function used to identify documents that employees have submitted
def edit_doc_submission(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        user_mod = User.objects.get(id=pk)
        for i in request.POST.getlist('docs'):
            doc_mod = models.onboarding_docs.objects.get(id=i)
            onboard_doc = models.doc_submit_req.objects.filter(doc=doc_mod, employee=user_mod).update(submitted=True)
        return HttpResponseRedirect(reverse('review_sub_docs'))
    else:    
        name = User.objects.get(id=pk)
        name_print = name.first_name + ' ' + name.last_name
        edit_sub_require = forms.edit_sub_docs(pk=pk)
        context = {'name_print': name_print,
                   'edit_sub_require': edit_sub_require,
        }
        return render(request, 'training_docs/edit_doc_submission.html', context)

def employee_doc_submitted(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        emp = request.POST.get('employee')
        doc = request.POST.get('doc')
        row = models.doc_submit_req.objects.create(employee_id=emp, doc_id=doc)
        return HttpResponseRedirect(reverse('review_ack_docs'))
    sub_form = forms.training_doc_submitted()
    context = {'sub_form': sub_form}
    return render(request, 'training_docs/employee_doc_submitted.html', context)
