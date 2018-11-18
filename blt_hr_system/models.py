# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.urls import reverse
import datetime
import uuid
from django.conf import settings

class training_docs(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    upload_name = models.CharField(max_length=200, null=True, blank=True)
    upload = models.FileField(upload_to='media/training_docs/', null=True, blank=True)

class employee_group(models.Model):
    # the group each employee belongs to e.g. Office Staff, Site Super, Foreman
    group_name = models.CharField(max_length=200)
    group_description = models.CharField(max_length=500)

class vaction_allocation(models.Model):
    # contains information pretaining to each employee
    employee_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    alloc_absence_days = models.PositiveIntegerField(blank=False, null=False, default=0)
    carr_over_days = models.PositiveIntegerField(blank=False, null=False, default=0)
    yr = models.PositiveIntegerField(blank=False, null=False, default=0)
    is_increased = models.BooleanField(default=False, blank=True)
    increased_days = models.PositiveIntegerField(blank=False, null=True, default=0)
    increased_date = models.DateField(null=True, blank=False)

class certification(models.Model):
    # name of the certs that will be tracked
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=1000, null=True)

class company_info(models.Model):
    # regions that the company has, used for holidays
    region = models.CharField(max_length=200)

class employee(models.Model):
    # contains information pretaining to each employee
    email = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    birth_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    employee_group = models.ForeignKey('employee_group', on_delete=models.SET_NULL, null=True)
    manager = models.ForeignKey('employee', on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey('company_info', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False, blank=True)

class holiday(models.Model):
    # holidays that the company has, used for absence date calculations
    name = models.CharField(max_length=200)
    date = models.DateField(null=False, blank=False)
    region = models.ManyToManyField('company_info')

class cert_group(models.Model):
    # The certs that each employee group requires
    employee_group = models.ForeignKey('employee_group', on_delete=models.SET_NULL, null=True)
    cert_req = models.ManyToManyField('certification', 
        help_text='Select a required certification for this group')

class employee_certification(models.Model):
    # information for certifications submitted by employees to be approved by admin
    employee_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cert_name = models.ForeignKey('certification', on_delete=models.SET_NULL, null=True)
    date_submitted = models.DateField(auto_now_add=True)
    acq_date = models.DateField(null=False, blank=False)
    exp_date = models.DateField(null=True, blank=True)
    cert_doc = models.CharField(max_length=500)
    is_approved = models.BooleanField(default=False, blank=True)
    approval_date = models.DateField(null=True, blank=True)

class employee_absence(models.Model):
    # information for absences submitted by employees to be approved by management
    employee_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    yr1 = models.PositiveIntegerField(blank=False, null=False, default=0)
    yr1_num_days = models.PositiveIntegerField(blank=False, null=False, default=0)
    yr2 = models.PositiveIntegerField(blank=False, null=False, default=0)
    yr2_num_days = models.PositiveIntegerField(blank=False, null=False, default=0)
    num_days_prior_apr_31 = models.PositiveIntegerField(blank=False, null=False, default=0)
    ABSCENCES = (('Sick','Sick'), ('Vacation','Vacation'), ('Bereavement','Bereavement'), 
        ('Time off without pay','Time off without pay'), ('Maternity or Paternity','Maternity or Paternity'),
        ('Other', 'Other'))
    absence_type = models.CharField(max_length=200, choices=ABSCENCES)
    absence_reason = models.CharField(max_length=1000)
    date_submitted = models.DateField(auto_now_add=True)
    is_manager_approved = models.BooleanField(default=False, blank=True)
    date_approved = models.DateField(null=False, blank=False)
    manager_comment = models.CharField(max_length=1000)