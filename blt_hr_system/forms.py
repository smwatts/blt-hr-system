from django import forms
from .models import employee_absence, employee_certification
from django.contrib.admin import widgets
from bootstrap_datepicker.widgets import DatePicker

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
        fields = ['acq_date', 'cert_doc']
        widgets = {
            'acq_date': DateInput(),
        }

class cert_approval(forms.ModelForm):
    class Meta:
        model = employee_certification
        fields = ['is_approved']