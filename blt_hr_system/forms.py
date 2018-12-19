from django import forms
from .models import employee_absence, employee_certification, training_docs, Profile, company_info, certification
from django.contrib.admin import widgets
from django.forms.widgets import HiddenInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class add_certification(forms.ModelForm):
    class Meta:
        model = certification
        fields = ['name', 'description', 'expiration_yrs']
        help_texts = {'expiration_yrs': "If the certification does not expire, leave the value as 0.",}

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
        fields = ['acq_date', 'cert_name', 'upload']
        widgets = {
            'acq_date': DateInput(),
        }

class cert_approval(forms.ModelForm):
    class Meta:
        model = employee_certification
        fields = ['is_approved']

class training_docs_submit(forms.ModelForm):
    class Meta:
        model = training_docs
        exclude = ['uploaded_by',]
        labels = {
        "upload_name": "Training document name",
        "upload" : "Select the training document"
        }

class remove_doc(forms.Form): 
    document_name = forms.ModelChoiceField(queryset=training_docs.objects.order_by('upload_name').values_list('upload_name', flat=True).distinct())

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('location', 'position')

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter the BLT email address for this account.')
    start_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'start_date', 'password1', 'password2', )
