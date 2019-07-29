from django import forms
from .models import employee_absence, employee_certification, training_docs, Profile, \
    company_info, certification, onboarding_cat, doc_submit_req, doc_read, perf_forms, \
    perf_cat, sage_jobs, hourly_timesheet, emp_perf_forms
from django.contrib.admin import widgets
from django.forms.widgets import HiddenInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q

class ack_doc(forms.ModelForm):
    class Meta:
        model = doc_read
        fields = ['doc']
        labels = {'doc': "Read acknowledgement",
        }
        help_texts = {'doc': "Check this box if you have read the onboarding / training document.",
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

class add_onboarding_cat(forms.ModelForm):
    class Meta:
        model = onboarding_cat
        fields = ['name']
        labels = {'name':"Onboarding document category name",
        }

class edit_ack_require(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['read_req']
        widgets = {
            'read_req': forms.CheckboxSelectMultiple,
        }
        labels = {'read_req':"Acknowledgement Requirement",
        }
        help_texts = {'read_req':"Please select all training categories this employee has to acknowledge training documents for."
        }

class edit_sub_require(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['submit_req']
        widgets = {
            'submit_req': forms.CheckboxSelectMultiple,
        }
        labels = {'submit_req':"Submission Requirement",
        }
        help_texts = {'submit_req':"Please select all training categories this employee has to submit training documents for."
        }

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
    class Meta:
        model = training_docs
        fields = ['upload', 'upload_name','onboarding_cat',]
        labels = {
            "upload_name": "Training document name",
            "upload": "Select the training document",
            "onboarding_cat": "Onboarding document?",
        }
        help_texts = {
            "onboarding_cat": "If this is a document that will be tracked for employee onbaording, please select the category name. Otherwise please leave this field blank.",
        }

class remove_doc(forms.ModelForm): 
    delete_document = forms.BooleanField(required=False,
        label='Are you sure you want to delete this document?',
        help_text='If you select the box above and click save the document and all document history will be deleted from the system.')
    class Meta:
        model = training_docs
        fields = ['id',]
        widgets = {'id': forms.HiddenInput(),
        }
        
# ---------------------------------------------------------------------
# EMPLOYEE PROFILE
# ---------------------------------------------------------------------

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
        fields = ['location', 'position', 'manager', 'start_date']
        fields_required = ['location', 'position', 'start_date']
        help_texts = {
            'start_date': 'Format: YYYY-MM-DD.',
        }

class SignUpForm(UserCreationForm):
    office_staff = forms.BooleanField(required=False,
        help_text='Select if this employee must complete a bi-weekly timesheet.')
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(max_length=254, required=True,
        help_text='Required. Enter the email address for that will be associated with this users account.')
    position = forms.CharField(max_length=50, required=True,
        help_text='Enter the name of the employees postiion.')
    location = forms.ModelChoiceField(queryset=company_info.objects.all().order_by('location'),
         help_text='Select the primary location for the employee.')
    start_date = forms.DateField(help_text='Format: YYYY-MM-DD.')
    certifications = forms.ModelMultipleChoiceField(queryset=certification.objects.order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='Select all required certifications for this employee.')
    onbaording_read = forms.ModelMultipleChoiceField(queryset=onboarding_cat.objects.order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='Select all documents this employee must acknowledge as read.',
        label='Documents requiring acknowledge')
    onbaording_submit = forms.ModelMultipleChoiceField(queryset=onboarding_cat.objects.order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='Select all documents this employee must submit to HR.',
        label='Documents requiring submission')
    perf_cat = forms.ModelChoiceField(required=False,
        queryset=perf_cat.objects.all().order_by('name'),
        help_text='Please select the performance review category this user will be associated with.')
    absence_allocation_annually = forms.IntegerField(required=False, initial=0,
        help_text='Enter the number of days for absences allocated for the employee annually. If the employee does not have allocated absence days, enter 0.')
    manager = forms.ModelChoiceField(required=False,
        queryset=Profile.objects.all().filter(user__is_active=True).exclude(user__username='system_admin').order_by('user__first_name'),
        help_text='The manager selected will be responsible for approving absence requests and conducting performance reviews.')
    absence_allocation_annually = forms.IntegerField(required=False, initial=0,
        help_text='Enter the number of days for absences allocated for the employee annually. If the employee does not have allocated absence days, enter 0.')
    sick_day_allocation_annually = forms.IntegerField(required=False, initial=0,
        help_text='Enter the number of sick days allocated for the employee annually. If the employee does not have allocated sick days, enter 0.')
    password = User.objects.make_random_password()
    password1 = forms.CharField(
        widget=forms.HiddenInput(),
        initial=password,
        required=False
    )
    password2 = forms.CharField(
        widget=forms.HiddenInput(),
        initial=password,
        required=False
    )
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'position', 'location', 'start_date', 'office_staff',
            'certifications', 'manager', 'absence_allocation_annually', 'password1', 'password2',)

# ---------------------------------------------------------------------
# ABSENCES
# ---------------------------------------------------------------------

class upload_holidays(forms.Form):
    location = forms.ModelChoiceField(queryset=company_info.objects.all().order_by('location'),
        help_text='Select the location the holidays are for.',
        required=True)
    docfile = forms.FileField(
        label='Select a csv file',
        help_text='The csv file must contain a Holiday Names and Holiday Dates column.',
        required=True
    )

# ---------------------------------------------------------------------
# TRAINING DOCS
# ---------------------------------------------------------------------

class training_doc_submitted(forms.Form):
    employee = forms.ModelChoiceField(required=True,
        queryset=Profile.objects.all().filter(user__is_active=True).exclude(user__username='system_admin').order_by('user__first_name'),
        help_text='Select the employee that has submitted the training document.')
    doc = forms.ModelChoiceField(required=True,
        queryset=training_docs.objects.all().order_by('upload_name'),
        help_text='Select the submitted training document.')

# ---------------------------------------------------------------------
# PERFORMANCE FORMS
# ---------------------------------------------------------------------

# submit a performance form
class perf_forms_submit(forms.ModelForm):
    class Meta:
        model = perf_forms
        fields = ['upload', 'upload_name', 'perf_cat']
        fields_required = ['upload', 'upload_name', 'perf_cat']
        labels = {
            "upload_name": "Performance form name",
            "upload": "Select the performance form",
            "perf_cat": "Select the performance review category"
        }
    def __init__(self, *args, **kwargs):
        super(perf_forms_submit, self).__init__(*args, **kwargs)
        self.fields['upload'].required = True
        self.fields['upload_name'].required = True
        self.fields['perf_cat'].required = True

# update an employee's performace category
class edit_emp_perf_cat(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['perf_cat']
        help_texts = {
            'perf_cat': 'Select the performance category for this employee.',
        }
        labels = {
            'perf_cat': 'Performance Category'
        }

# edit the names of performance categories
class add_edit_perf_cats(forms.ModelForm):
    class Meta:
        model = perf_cat
        fields = ['name']
        help_texts = {
            'name': 'Edit the performance category.',
        }

# ---------------------------------------------------------------------
# TIMESHEETS
# ---------------------------------------------------------------------

class upload_jobs(forms.Form):
    docfile = forms.FileField(
        label='Select a csv file',
        help_text='The csv file must contain a "Job" and "Description" column.',
        required=True
    )

class sage_job_update(forms.ModelForm):
    class Meta:
        model = sage_jobs
        fields = ('job_id', 'job_desc')
        labels = {
            'job_id': 'Job ID',
            'job_desc':'Job Description',
        }
    def __init__(self, *args, **kwargs):
        super(sage_job_update, self).__init__(*args, **kwargs)
        self.fields['job_id'].disabled = True

class edit_office_staff(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['office_staff']
        help_texts = {
            'office_staff': 'Select if this employee should be considered an office staffer with timesheets.',
        }
        labels = {
            'perf_cat': 'Office Staffer?'
        }

class timesheet_select(forms.ModelForm):
    class Meta:
        model = hourly_timesheet
        fields = ['ts_period',]
        help_texts = {
            'ts_period':'Please select the timesheet period that you will be submitting'
        }
        labels = {
            'ts_period':'Timesheet for the period'
        }

class select_jobs(forms.Form):
    Sage_jobs = forms.ModelMultipleChoiceField(queryset=sage_jobs.objects.order_by('job_id'),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='Select all jobs that have been worked on throughout this period.')

class hourly_ts(forms.ModelForm):
    class Meta:
        model = hourly_timesheet
        fields = ['sage_job', 'hours', 'description', 'is_finalized']
        widgets = {'is_finalized': forms.HiddenInput()}
    def __init__(self, *args, **kwargs):
        super(hourly_ts, self).__init__(*args, **kwargs)
        self.fields['sage_job'].disabled = True

class timesheet_export(forms.ModelForm):
    class Meta:
        model = hourly_timesheet
        fields = ['ts_period',]
        help_texts = {
            'ts_period':'Please select the timesheet period that you would like to export',
        }
        labels = {
            'ts_period':'Timesheet for the period',
        }

class timesheet_emp(forms.Form):
    employee_id = forms.ModelChoiceField(required=True,
        queryset=Profile.objects.all().filter(office_staff=True).order_by('user__first_name'),
        help_text='Select the employee.',
        label='Employee')

class timesheet_emp_ts(forms.ModelForm):
    employee_id = forms.ModelChoiceField(required=True,
        queryset=Profile.objects.all().filter(office_staff=True).order_by('user__first_name'),
        help_text='Select the employee.',
        label='Employee')
    class Meta:
        model = hourly_timesheet
        fields = ['employee_id', 'ts_period']
        help_texts = {
            'employee_id':'Please select an employee',
            'ts_period':'Please select a timesheet period',
        }
        labels = {
            'employee_id':'Employee',
            'ts_period':'Timesheet for the period',
        }

# ---------------------------------------------------------------------
# PERFORMANCE REVIEW
# ---------------------------------------------------------------------

class submit_perf(forms.ModelForm):
    class Meta:
        model = emp_perf_forms
        fields = ['upload', 'upload_name', 'year']
        labels = {
            'upload': "Select your completed performance review",
            'upload_name': "Specify the filename for this performance review",
            'year': 'Select the year for this performance form'
        }

class manager_submit_perf(forms.ModelForm):
    class Meta:
        model = emp_perf_forms
        fields = ['manager_upload', 'manager_upload_name', 'manager_uploaded_at',
                    'employee', 'upload_name', 'upload', 'year'
        ]
        labels = {
            'manager_upload': "Select your completed performance review",
            'manager_upload_name': "Select the name of the performance review",
            'upload_name':"Performance review name",
            'upload':"Performance review",
        }
        widgets = {'manager_uploaded_at': forms.HiddenInput(),
        }
        fields_required = ['manager_upload_name', 'manager_upload']
    def __init__(self, *args, **kwargs):
        super(manager_submit_perf, self).__init__(*args, **kwargs)
        self.fields['year'].disabled = True
        self.fields['employee'].disabled = True
        self.fields['upload'].disabled = True
        self.fields['upload_name'].disabled = True
        self.fields['manager_upload_name'].required = True
        self.fields['manager_upload'].required = True
        self.fields['manager_uploaded_at'].required = False

# ---------------------------------------------------------------------
# ADMIN ACOCUNT ACCESS
# ---------------------------------------------------------------------

class edit_system_access(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['access']
        widgets = {
            'access': forms.CheckboxSelectMultiple,
        }
