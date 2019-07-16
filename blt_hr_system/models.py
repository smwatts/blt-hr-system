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
        extension = os.path.splitext(filename)[1]
        return self.path % (uuid.uuid4(), extension)

def cert_doc_path(instance, filename):
    extension = os.path.splitext(filename)[1]
    return 'media/certification/{username}/{filename}{extension}'.format(
        username=instance.employee_id, filename=uuid.uuid4(), extension=extension)

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
    # name of the certs that will be tracked and their expirations
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, null=True)
    expiration_yrs = models.PositiveIntegerField(blank=False, null=True, default=0)
    def __str__(self):
        return self.name

class company_info(models.Model):
    # locations that the company has, used for holidays
    location = models.CharField(max_length=200, blank=False, null=False)
    def __str__(self):
        return self.location

class Profile(models.Model):
    # contains information pretaining to each employee
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=200, null=True)
    birth_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    manager = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey('company_info', on_delete=models.SET_NULL, null=True)
    certs = models.ManyToManyField(certification)
    office_staff = models.BooleanField(default=False, blank=True)
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

# ---------------------------------------------------------------------
# TRAINING DOCS
# ---------------------------------------------------------------------

# List of all onboarding categories
class onboarding_cat(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name
        
# List of all training docs stored in the system
# Includes if the training doc is active & the onboarding category for the doc
class training_docs(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    upload_name = models.CharField(max_length=200, null=False, blank=False)
    upload = models.FileField(upload_to=RandomFileName('media/training_docs/'), null=False, blank=False)
    active_doc = models.BooleanField(default=False, blank=True)
    onboarding_cat = models.ForeignKey(onboarding_cat, on_delete=models.SET_NULL, null=True, blank=True) 
    def __str__(self):
        return self.upload_name

# To delete documents
# This will not be used - docs will instead be turned "inactive"
@receiver(models.signals.post_delete, sender=training_docs)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.upload.delete(save=False)

# For each user, their required onboarding category is specified here
# Each doc in the onboarding category that's read will be listed here
class doc_read_req(models.Model):
    read = models.ManyToManyField(training_docs)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    onboarding_cat = models.ForeignKey(onboarding_cat, on_delete=models.CASCADE, null=True) 

# For each user, their required onboarding category is specified here
# Each doc in the onboarding category that's submitted will be listed here
class doc_submit_req(models.Model):
    submitted = models.ManyToManyField(training_docs)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    onboarding_cat = models.ForeignKey(onboarding_cat, on_delete=models.CASCADE, null=True) 

# ---------------------------------------------------------------------
# EMPLOYEE PROFILE
# ---------------------------------------------------------------------

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
    location = models.ManyToManyField('company_info')

class employee_certification(models.Model):
    # information for certifications submitted by employees to be approved by admin
    employee_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cert_name = models.ForeignKey('certification', on_delete=models.CASCADE, null=False, blank=False)
    acq_date = models.DateField(null=False, blank=False)
    exp_date = models.DateField(null=True, blank=True)
    upload = models.FileField(upload_to=cert_doc_path, null=False, blank=False)
    is_approved = models.BooleanField(default=False, blank=True)

@receiver(models.signals.post_delete, sender=employee_certification)
def remove_cert_from_s3(sender, instance, using, **kwargs):
    instance.upload.delete(save=False)

# ---------------------------------------------------------------------
# ABSENCES
# ---------------------------------------------------------------------

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
    is_admin_approved = models.BooleanField(default=False, blank=True)
    date_approved_manager = models.DateField(null=False, blank=False)
    date_approved_admin = models.DateField(null=False, blank=False)
    manager_comment = models.CharField(max_length=1000)
    admin_comment = models.CharField(max_length=1000)

# ---------------------------------------------------------------------
# TIMESHEETS
# ---------------------------------------------------------------------

class timesheets(models.Model):
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)

class sage_jobs(models.Model):
    job_id = models.CharField(max_length=200)
    job_desc = models.CharField(max_length=1000)

class hourly_timesheet(models.Model):
    employee_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sage_job = models.ForeignKey('sage_jobs', on_delete=models.CASCADE, null=False, blank=False)
    hours = models.PositiveIntegerField(blank=False, null=False, default=0)
    description = models.CharField(max_length=1000, blank=True)
