from django import forms
from .models import employee_absence, employee_certification

class absence_request(forms.ModelForm):
    class Meta:
        model = employee_absence
        fields = ['start_date', 'end_date', 'abs_type', 'abs_reason']

class absence_approval(forms.ModelForm):
    class Meta:
        model = employee_absence
        fields = ['is_manager_approved', 'manager_comment']

class cert_request(forms.ModelForm):
    class Meta:
        model = employee_certification
        fields = ['cert_name', 'acq_date', 'cert_doc']

class cert_approval(forms.ModelForm):
    class Meta:
        model = employee_certification
        fields = ['is_approved']