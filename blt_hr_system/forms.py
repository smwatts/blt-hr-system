from django import forms
from .models import employee_absence, employee_certification, training_docs, Profile, company_info, certification, onboarding_docs, doc_read_req, doc_submit_req
from django.contrib.admin import widgets
from django.forms.widgets import HiddenInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ack_doc(forms.ModelForm):
    class Meta:
        model = doc_read_req
        fields = ['read']
        labels = {'read': "Read acknowledgement",
        }
        help_texts = {'read': "Check this box if you have read the onboarding / training document.",
        }

class review_cert(forms.ModelForm):
    message = forms.CharField(max_length=500, required=False)
    class Meta:
        model = employee_certification
        fields = ['is_approved', 'employee_id', 'cert_name', 'message']
        help_texts = {'message':"If required, enter a message that will be sent to the certification submitter.",
                      'is_approved': "Check this box if you approve the certification, otherwise the certification will be rejected.",
        }
        labels = {'message':"Add a message",
                  'is_approved':"Approved?",
        }
        widgets = {'employee_id': forms.HiddenInput(),
                   'cert_name': forms.HiddenInput()
        }

class edit_system_certs(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['certs']
        widgets = {
            'certs': forms.CheckboxSelectMultiple,
        }

class add_birth_date(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['birth_date']
        help_texts = {'birth_date':"Format: YYYY-MM-DD"}
        
class add_certification(forms.ModelForm):
    class Meta:
        model = certification
        fields = ['name', 'description', 'expiration_yrs']
        help_texts = {'expiration_yrs': "If the certification does not expire, enter 0.",}

class add_onboarding_doc(forms.ModelForm):
    class Meta:
        model = onboarding_docs
        fields = ['name', 'doc']
        help_texts = {'name': "This is a generic name that will be used for the onboarding / training document and will prevail through document changes / updates.",
                      'doc':"Don't see the right document listed? It may already be assigned to an onboarding / training document.",
        }
        labels = {'name':"Onboarding / training document name",
                  'doc':"Uploaded document"
        }

class edit_ack_require(forms.Form):
    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super(edit_ack_require,self).__init__(*args,**kwargs)
        doc_list = list(doc_read_req.objects.all().filter(employee=pk).values_list('doc', flat = True))
        self.fields['docs'] = forms.ModelMultipleChoiceField(
            queryset=onboarding_docs.objects.all().order_by('name'),
            label="Required Onboarding / training documents", 
            help_text="Please select all onboarding / training documents that require acknowledgement",
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            initial=doc_list)

class edit_sub_require(forms.Form):
    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super(edit_sub_require,self).__init__(*args,**kwargs)
        doc_list = list(doc_submit_req.objects.all().filter(employee=pk).values_list('doc', flat = True))
        self.fields['docs'] = forms.ModelMultipleChoiceField(
            queryset=onboarding_docs.objects.all().order_by('name'),
            label="Required Onboarding / training documents", 
            help_text="Please select all onboarding / training documents that require submission",
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            initial=doc_list)

class edit_sub_docs(forms.Form):
    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super(edit_sub_docs,self).__init__(*args,**kwargs)
        req_doc = list(doc_submit_req.objects.all().filter(employee=pk, submitted=False).values_list('doc', flat = True))
        self.fields['docs'] = forms.ModelMultipleChoiceField(
            queryset=onboarding_docs.objects.all().filter(id__in=req_doc).order_by('name'),
            label="Update documents", 
            help_text="Please select all documents that have been submitted",
            required=False,
            widget=forms.CheckboxSelectMultiple()
            )

class submit_company_info(forms.ModelForm):
    class Meta:
        model = company_info
        fields = ['location']
        help_texts = {'location': "Each employee will be assigned to a company location entered.",}

class DateInput(forms.DateInput):
    input_type = 'date'

class absence_request(forms.ModelForm):
    class Meta:
        model = employee_absence
        fields = ['start_date', 'end_date', 'absence_type', 'absence_reason']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }

class absence_approval(forms.ModelForm):
    class Meta:
        model = employee_absence
        fields = ['is_manager_approved', 'manager_comment']

class cert_request(forms.ModelForm):
    class Meta:
        model = employee_certification
        # add the cert name
        exclude = ['employee_id', 'exp_date', 'is_approved',]
        widgets = {
            'acq_date': DateInput(),
        }
        labels = {
            'upload': "Select a copy of your certification",
            'acq_date': "Date acquired",
            'cert_name': "Certification",
        }
        help_texts = {
            'acq_date': "Format: YYYY-MM-DD.",
            'cert_name': "Please note, if this certification is approved it will replace the previous certifications of this type.",
        }

class cert_approval(forms.ModelForm):
    class Meta:
        model = employee_certification
        fields = ['is_approved']

class training_docs_submit(forms.ModelForm):
    onbard_doc = forms.ModelChoiceField(
        queryset=onboarding_docs.objects.all().order_by('name'),
        label="Onboarding / training document?", 
        help_text="If this is a document that will be tracked for employee onbaording / training, please select the tracking name. Otherwise please leave this field blank",
        initial='',
        required=False)
    update_read = forms.BooleanField(
        required=False, 
        label="Re-acknowledge required",
        help_text="For employees who are required to acknowledge they have read this onbaording / training document, they will have to re-acknowledge this new document.",
        initial=False)
    update_submit = forms.BooleanField(
        required=False, 
        label="Re-submit required",
        help_text="For employees who are required to submit this onbaording / training document, they will have to re-submit this new document.",
        initial=False)
    class Meta:
        model = training_docs
        fields = ['upload', 'upload_name',]
        labels = {
            'upload_name': "Training document name",
            'upload' : "Select the training document",
        }

class remove_doc(forms.Form): 
    document_name = forms.ModelChoiceField(queryset=training_docs.objects.all().order_by('upload_name'), 
        required=True)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_active')
        labels = {
            "is_active": "Current employee"
        }
        help_texts = {
            "is_active": "If the employee no longer works at BLT, they will not longer have access to the system"
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('location', 'position', 'manager')

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(max_length=254, required=True,
        help_text='Required. Enter the email address for that will be associated with this users account.')
    position = forms.CharField(max_length=50, required=False,
        help_text='Enter the name of the employees postiion.')
    location = forms.ModelChoiceField(queryset=company_info.objects.all().order_by('location'),
         help_text='Select the primary location for the employee.')
    start_date = forms.DateField(help_text='Format: YYYY-MM-DD.')
    certifications = forms.ModelMultipleChoiceField(queryset=certification.objects.order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='Select all required certifications for this employee.')
    onbaording_read = forms.ModelMultipleChoiceField(queryset=onboarding_docs.objects.order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='Select all documents this employee must acknowledge as read.',
        label='Documents requiring acknowledge')
    onbaording_submit = forms.ModelMultipleChoiceField(queryset=onboarding_docs.objects.order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='Select all documents this employee must submit to HR.',
        label='Documents requiring submission')
    manager = forms.ModelChoiceField(queryset=Profile.objects.all().filter(user__is_active=True).exclude(user__username='system_admin').order_by('user__first_name'),
        help_text='The manager selected will be responsible for approving absence requests and conducting performance reviews.')
    absence_allocation_annually = forms.IntegerField(required=True, initial=0,
        help_text='Enter the number of days for absences allocated for the employee annually. If the employee does not have allocated absence days, enter 0.')
    sick_day_allocation_annually = forms.IntegerField(required=True, initial=0,
        help_text='Enter the number of sick days allocated for the employee annually. If the employee does not have allocated sick days, enter 0.')
    password = User.objects.make_random_password()
    password1 = forms.CharField(
        widget=forms.HiddenInput(),
        initial=password
    )
    password2 = forms.CharField(
        widget=forms.HiddenInput(),
        initial=password
    )
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'position', 'location', 'start_date', 
            'certifications', 'manager', 'absence_allocation_annually', 'password1', 'password2',)
