# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.urls import reverse
import datetime
import uuid
from django.conf import settings
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.deconstruct import deconstructible

@deconstructible
class RandomFileName(object):
    def __init__(self, path):
        self.path = os.path.join(path, "%s%s")
    def __call__(self, _, filename):
        # @note It's up to the validators to check if it's the correct file type in name or if one even exist.
        extension = os.path.splitext(filename)[1]
        return self.path % (uuid.uuid4(), extension)

class training_docs(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    upload_name = models.CharField(max_length=200, null=True, blank=True)
    upload = models.FileField(upload_to=RandomFileName('media/training_docs/'), null=True, blank=True)

@receiver(models.signals.post_delete, sender=training_docs)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.upload.delete(save=False)

class employee_group(models.Model):
    # the group each employee belongs to e.g. Office Staff, Site Super, Foreman
    group_name = models.CharField(max_length=200, null=True)
    group_description = models.CharField(max_length=500, null=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

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

class Profile(models.Model):
    # contains information pretaining to each employee
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=200, null=True)
    birth_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    employee_group = models.ForeignKey('employee_group', on_delete=models.SET_NULL, null=True)
    manager = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=False, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

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