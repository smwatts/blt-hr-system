# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.urls import reverse
import datetime
import uuid

class employee_groups(models.Model):
    # the group each employee belongs to e.g. Office Staff, Site Super, Foreman
    group_name = models.CharField(max_length=200)
    group_description = models.CharField(max_length=500)
    def __str__(self):
        return self.field_name
    def get_absolute_url(self):
        return reverse('employee-group-details', args=[str(self.id)])
        
class employees(models.Model):
    # contains information pretaining to each employee
    email = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    birth_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    alloc_absence_days = models.PositiveIntegerField(blank=False, null=False, default=0)
    carr_over_days = models.PositiveIntegerField(blank=False, null=False, default=0)
    employee_group = models.ForeignKey('employee_groups', on_delete=models.SET_NULL, null=True)
    manager = models.ForeignKey('employees', on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.field_name
    def get_absolute_url(self):
        return reverse('employee-details', args=[str(self.id)])

class certs(models.Model):
    # name of the certs that will be tracked
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.field_name

class company_info(models.Model):
    # regions that the company has, used for holidays
    region = models.CharField(max_length=200)
    def __str__(self):
        return self.field_name

class holidays(models.Model):
    # holidays that the company has, used for absence date calculations
    name = models.CharField(max_length=200)
    date = models.DateField(null=False, blank=False)
    region = models.ForeignKey('company_info', on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.field_name

class cert_groups(models.Model):
    # The certs that each employee group requires
    employee_group = models.ForeignKey('employee_groups', on_delete=models.SET_NULL, null=True)
    cert_req = models.ManyToManyField('certs', 
        help_text='Select a required certification for this group')
    def __str__(self):
        return self.field_name
    def get_absolute_url(self):
        return reverse('cert-group-details', args=[str(self.id)])

class cert_requests(models.Model):
    # requests for certifications submitted by employees to be approved by admin
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, 
        help_text="Unique ID for each certification request")
    employee_id = models.ForeignKey('employees', on_delete=models.SET_NULL, null=True)
    cert_name = models.ForeignKey('certs', on_delete=models.SET_NULL, null=True)
    date_submitted = models.DateField(auto_now_add=True)
    acq_date = models.DateField(null=False, blank=False)
    exp_date = models.DateField(null=True, blank=True)
    cert_doc = models.CharField(max_length=500)
    is_approved = models.BooleanField(default=False, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.field_name
    def get_absolute_url(self):
        return '{0} ({1})'.format(self.id,self.employees.email)

class absence_requests(models.Model):
    # requests for absences submitted by employees to be approved by management
    employee_id = models.ForeignKey('employees', on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    yr1 = models.PositiveIntegerField(blank=False, null=False, default=0)
    yr1_num_days = models.PositiveIntegerField(blank=False, null=False, default=0)
    yr2 = models.PositiveIntegerField(blank=False, null=False, default=0)
    yr2_num_days = models.PositiveIntegerField(blank=False, null=False, default=0)
    abs_type = models.CharField(max_length=200)
    abs_reason = models.CharField(max_length=1000)
    date_submitted = models.DateField(auto_now_add=True)
    is_manager_approved = models.BooleanField(default=False, blank=True)
    date_approved = models.DateField(null=False, blank=False)
    manager_comment = models.CharField(max_length=1000)
    def __str__(self):
        return self.field_name
    def get_absolute_url(self):
        return '{0} ({1})'.format(self.id,self.employees.email)