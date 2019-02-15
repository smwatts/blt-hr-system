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
    sub_missing = models.doc_submit_req.objects.all().filter(employee=request.user, 
        submitted=False).values('doc__name', 'doc__doc__upload', 'doc__doc__upload_name', 'id')
    sub_complete = models.doc_submit_req.objects.all().filter(employee=request.user, 
        submitted=True).values('doc__name', 'doc__doc__upload', 'doc__doc__upload_name', 'id')
    ack_missing = models.doc_read_req.objects.all().filter(employee=request.user, 
        read=False).values('doc__name', 'doc__doc__upload', 'doc__doc__upload_name', 'id')
    ack_complete = models.doc_read_req.objects.all().filter(employee=request.user, 
        read=True).values('doc__name', 'doc__doc__upload', 'doc__doc__upload_name', 'id')
    context = {'sub_missing': sub_missing,
               'sub_complete': sub_complete,
               'ack_missing': ack_missing,
               'ack_complete': ack_complete,}
    return render(request, 'training_docs/onboarding_training_docs.html', context) 

# Employee function to acknowledge when a form has been read
def ack_doc_read(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    doc_read = models.doc_read_req.objects.get(id=pk)
    if request.user.id != doc_read.employee_id:
        return HttpResponseRedirect(reverse('home'))
    else:
        if request.method == 'POST':
            ack_form = forms.ack_doc(request.POST, instance=doc_read)
            if ack_form.is_valid():
                ack_form.save()
                messages.success(request, 'The document was successfully acknowledged!')
                return HttpResponseRedirect(reverse('onboarding_training_docs'))
        else:
            ack_form = forms.ack_doc(instance=doc_read)
            doc_vals = models.doc_read_req.objects.all().filter(id=pk).values('doc__name', 
                'doc__doc__upload', 'doc__doc__upload_name')
            context = {'ack_form': ack_form,
                       'doc_vals': doc_vals,
            }
            return render(request, 'training_docs/ack_doc_read.html', context) 

# ------------------------------------------------------------------
# ADMIN FUNCTIONS
# ------------------------------------------------------------------

# Admin function to remove documents from the system
# TO DO: change the functionality to "active/inactie" instead of removing docs
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
            return render(request, 'training_docs/delete_training_doc.html', context) 
    form = forms.remove_doc()
    documents = models.training_docs.objects.all()
    message = False
    context = {'documents': documents,
                'form': form,
                'message': message,}
    return render(request, 'training_docs/delete_training_doc.html', context)  

# Admin function to add a new training documents
# TO DO: Change the functionality to remove the "re-ack"/"re-submit"
#        If the doc is an "onboarding" doc then it must be "re-ack"/"re-submit"
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
    return render(request, 'training_docs/training_material.html', context)

# Admin function to create onboarding form categories
# TO DO: Remove the 1:1 relationship between a training document and
#        an onboarding form
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
            document_inst = models.training_docs.objects.get(id=request.POST.get('doc'))
            document_name = document_inst.upload_name
            doc_form = forms.add_onboarding_doc()
            doc_info = models.onboarding_docs.objects.all()
            context = {'doc_form': doc_form,
                       'doc_info' : doc_info,
                       'error_msg':error_msg,
                       'document_name':document_name,
            }
            return render(request, 'training_docs/manage_onboarding_docs.html', context)
    else:
        doc_form = forms.add_onboarding_doc()
        doc_info = models.onboarding_docs.objects.all()
        error_msg = False
        context = {'doc_form': doc_form,
                   'doc_info' : doc_info,
                   'error_msg':error_msg,}
    return render(request, 'training_docs/manage_onboarding_docs.html', context)

# Admin function to edit an onboarding category
# TO DO: Figure out what "editting an onboarding category" means
#        Can we remove docs from that category? What happens when we do?
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
            messages.success(request, 'The onboarding document was successfully updated!')
            return HttpResponseRedirect(reverse('manage_onboarding_docs'))
        else:
            error_msg = True
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
            return render(request, 'training_docs/edit_onboarding_docs.html', context)
    else:
        doc = models.onboarding_docs.objects.get(id=pk)
        doc_form = forms.add_onboarding_doc(instance=doc)
        context = {'doc_form': doc_form,}
        return render(request, 'training_docs/edit_onboarding_docs.html', context)

# Admin function to display the onboarding "ack" & "submit" requirements for all employees
def onboarding_requirement(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    sql = """
        WITH req_doc as (
            SELECT "blt_hr_system_doc_read_req"."employee_id" as employee_id,  
                array_agg("blt_hr_system_onboarding_docs"."name"
                    ORDER BY "blt_hr_system_onboarding_docs"."name" 
                    ASC) AS req_doc
            FROM "blt_hr_system_doc_read_req"
            LEFT JOIN "blt_hr_system_onboarding_docs"
                on "blt_hr_system_doc_read_req"."doc_id" = "blt_hr_system_onboarding_docs"."id"
            GROUP BY 1
        ),
            sub_doc as (
            SELECT "blt_hr_system_doc_submit_req"."employee_id" as employee_id,  
                array_agg("blt_hr_system_onboarding_docs"."name"
                    ORDER BY "blt_hr_system_onboarding_docs"."name" 
                    ASC) AS sub_doc
            FROM "blt_hr_system_doc_submit_req"
            LEFT JOIN "blt_hr_system_onboarding_docs"
                on "blt_hr_system_doc_submit_req"."doc_id" = "blt_hr_system_onboarding_docs"."id"
            GROUP BY 1
        ),
            users as (
            SELECT "auth_user"."id" as id, 
                   "auth_user"."first_name" as first_name, 
                   "auth_user"."last_name" as last_name
            FROM "auth_user"
            GROUP BY 1,2,3
        )
        SELECT users.id, 
               users.first_name, 
               users.last_name, 
               req_doc.req_doc,
               sub_doc.sub_doc  
        FROM users
        LEFT JOIN req_doc
            on users.id = req_doc.employee_id
        LEFT JOIN sub_doc 
            on users.id = sub_doc.employee_id
        ORDER BY 2,3
        """
    cursor = connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    context = {'data':data
    }
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
        doc_req = models.doc_read_req.objects.all().filter(employee=pk)
        user_mod = User.objects.get(id=pk)
        leave_alone = list(set(list(map(int,request.POST.getlist('docs')))) & 
            set(list(models.doc_read_req.objects.all().filter(employee=pk).values_list('doc__id', flat=True))))
        for u in doc_req:
            if int(u.doc_id) not in leave_alone:
                u.delete()
        for i in request.POST.getlist('docs'):
            if int(i) not in leave_alone:
                onboard_doc = models.onboarding_docs.objects.get(id=i)
                models.doc_read_req.objects.create(employee=user_mod, doc=onboard_doc, read=False)
        return HttpResponseRedirect(reverse('onboarding_requirement'))
    name = User.objects.get(id=pk)
    name_print = name.first_name + ' ' + name.last_name
    edit_ack_require = forms.edit_ack_require(pk=pk)
    context = {'name_print': name_print,
                'edit_ack_require': edit_ack_require}
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
        doc_req = models.doc_submit_req.objects.all().filter(employee=pk)
        user_mod = User.objects.get(id=pk)
        leave_alone = list(set(list(map(int,request.POST.getlist('docs')))) & 
            set(list(models.doc_submit_req.objects.all().filter(employee=pk).values_list('doc__id', flat=True))))
        for u in doc_req:
            if int(u.doc_id) not in leave_alone:
                u.delete()
        for i in request.POST.getlist('docs'):
            if int(i) not in leave_alone:
                onboard_doc = models.onboarding_docs.objects.get(id=i)
                models.doc_submit_req.objects.create(employee=user_mod, doc=onboard_doc, submitted=False)
        return HttpResponseRedirect(reverse('onboarding_requirement'))
    name = User.objects.get(id=pk)
    name_print = name.first_name + ' ' + name.last_name
    edit_sub_require = forms.edit_sub_require(pk=pk)
    context = {'name_print': name_print,
                'edit_sub_require': edit_sub_require}
    return render(request, 'training_docs/edit_submission_req.html', context)

# Admin function to review each employee and the status of their "submitted" onboarding documents 
# This view will the display submitted & outstanding forms for each employee
def review_sub_docs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    sql = """
        WITH sub_doc_outstand as (
            SELECT "blt_hr_system_doc_submit_req"."employee_id" as employee_id,  
                array_agg("blt_hr_system_onboarding_docs"."name"
                    ORDER BY "blt_hr_system_onboarding_docs"."name" 
                    ASC) AS outstanding
            FROM "blt_hr_system_doc_submit_req"
            LEFT JOIN "blt_hr_system_onboarding_docs"
                on "blt_hr_system_doc_submit_req"."doc_id" = "blt_hr_system_onboarding_docs"."id"
            WHERE "blt_hr_system_doc_submit_req"."submitted" IS FALSE
            GROUP BY 1
        ),
            sub_doc_complete as (
            SELECT "blt_hr_system_doc_submit_req"."employee_id" as employee_id,  
                array_agg("blt_hr_system_onboarding_docs"."name"
                    ORDER BY "blt_hr_system_onboarding_docs"."name" 
                    ASC) AS complete
            FROM "blt_hr_system_doc_submit_req"
            LEFT JOIN "blt_hr_system_onboarding_docs"
                on "blt_hr_system_doc_submit_req"."doc_id" = "blt_hr_system_onboarding_docs"."id"
            WHERE "blt_hr_system_doc_submit_req"."submitted" IS TRUE
            GROUP BY 1
        ),
            users as (
            SELECT "auth_user"."id" as id, 
                   "auth_user"."first_name" as first_name, 
                   "auth_user"."last_name" as last_name
            FROM "auth_user"
            GROUP BY 1,2,3
        )
        SELECT users.id, 
               users.first_name, 
               users.last_name, 
               sub_doc_complete.complete,
               sub_doc_outstand.outstanding  
        FROM users
        LEFT JOIN sub_doc_outstand
            on users.id = sub_doc_outstand.employee_id
        LEFT JOIN sub_doc_complete 
            on users.id = sub_doc_complete.employee_id
        ORDER BY 5,2,3
        """
    cursor = connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    context = {'data':data
    }
    return render(request, 'training_docs/review_sub_docs.html', context)

# Admin function to review each employee and the status of their "ack" onboarding documents 
# This view will display the acknolwedged & outstanding forms each employee has
def review_ack_docs(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.user.username != "system_admin":
        return HttpResponseRedirect(reverse('home'))
    sql = """
        WITH ack_doc_outstand as (
            SELECT "blt_hr_system_doc_read_req"."employee_id" as employee_id,  
                array_agg("blt_hr_system_onboarding_docs"."name"
                    ORDER BY "blt_hr_system_onboarding_docs"."name" 
                    ASC) AS outstanding
            FROM "blt_hr_system_doc_read_req"
            LEFT JOIN "blt_hr_system_onboarding_docs"
                on "blt_hr_system_doc_read_req"."doc_id" = "blt_hr_system_onboarding_docs"."id"
            WHERE "blt_hr_system_doc_read_req"."read" IS FALSE
            GROUP BY 1
        ),
            ack_doc_complete as (
            SELECT "blt_hr_system_doc_read_req"."employee_id" as employee_id,  
                array_agg("blt_hr_system_onboarding_docs"."name"
                    ORDER BY "blt_hr_system_onboarding_docs"."name" 
                    ASC) AS complete
            FROM "blt_hr_system_doc_read_req"
            LEFT JOIN "blt_hr_system_onboarding_docs"
                on "blt_hr_system_doc_read_req"."doc_id" = "blt_hr_system_onboarding_docs"."id"
            WHERE "blt_hr_system_doc_read_req"."read" IS TRUE
            GROUP BY 1
        ),
            users as (
            SELECT "auth_user"."id" as id, 
                   "auth_user"."first_name" as first_name, 
                   "auth_user"."last_name" as last_name
            FROM "auth_user"
            GROUP BY 1,2,3
        )
        SELECT users.id, 
               users.first_name, 
               users.last_name, 
               ack_doc_complete.complete,
               ack_doc_outstand.outstanding  
        FROM users
        LEFT JOIN ack_doc_outstand
            on users.id = ack_doc_outstand.employee_id
        LEFT JOIN ack_doc_complete 
            on users.id = ack_doc_complete.employee_id
        ORDER BY 5,2,3
        """
    cursor = connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    context = {'data':data
    }
    return render(request, 'training_docs/review_ack_docs.html', context)

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
