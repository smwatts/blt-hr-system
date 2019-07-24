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

# List of all onboarding categories
class onboarding_cat(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Profile(models.Model):
    # contains information pretaining to each employee
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=200, null=True)
    birth_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    manager = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey('company_info', on_delete=models.SET_NULL, null=True)
    perf_cat = models.ForeignKey('perf_cat', on_delete=models.SET_NULL, null=True)
    certs = models.ManyToManyField(certification)
    read_req = models.ManyToManyField(onboarding_cat, related_name="read+")
    submit_req = models.ManyToManyField(onboarding_cat, related_name="submit+")
    office_staff = models.BooleanField(default=False, blank=True)
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

# ---------------------------------------------------------------------
# TRAINING DOCS
# ---------------------------------------------------------------------
        
# List of all training docs stored in the system
# Includes if the training doc is active & the onboarding category for the doc
class training_docs(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    upload_name = models.CharField(max_length=200, null=False, blank=False)
    upload = models.FileField(upload_to=RandomFileName('media/training_docs/'), null=False, blank=False)
    onboarding_cat = models.ForeignKey(onboarding_cat, on_delete=models.SET_NULL, null=True, blank=True) 
    def __str__(self):
        return self.upload_name

# To delete documents
# This will not be used - docs will instead be turned "inactive"
@receiver(models.signals.post_delete, sender=training_docs)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.upload.delete(save=False)

# Each doc that a user has acknowledged as read will live here
class doc_read(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doc = models.ForeignKey(training_docs, on_delete=models.CASCADE, null=True) 

# Each doc that a user has acknowledged as submitted will live here
class doc_submit_req(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doc = models.ForeignKey(training_docs, on_delete=models.CASCADE, null=True)


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
    ABSCENCES = (('Sick','Sick'), 
                ('Vacation','Vacation'), 
                ('Bereavement','Bereavement'), 
                ('Time off without pay','Time off without pay'), 
                ('Maternity or Paternity','Maternity or Paternity'),
                ('Other', 'Other'))
    absence_type = models.CharField(max_length=200, choices=ABSCENCES)
    absence_reason = models.CharField(max_length=1000)
    date_submitted = models.DateField(auto_now_add=True)
    is_manager_approved = models.BooleanField(default=False, blank=True)
    is_admin_approved = models.BooleanField(default=False, blank=True)
    date_approved_manager = models.DateField(null=False, blank=False)
    date_approved_admin = models.DateField(null=False, blank=False)
    manager_comment = models.CharField(max_length=1000, blank=True)
    admin_comment = models.CharField(max_length=1000, blank=True)

class company_holidays(models.Model):
    holiday_name = models.CharField(max_length=200)
    holiday_date = models.DateField(null=False, blank=False)
    location = models.ForeignKey('company_info', on_delete=models.CASCADE, null=False, blank=False)
    is_finalized = models.BooleanField(default=False, blank=False)
    upload_id = models.PositiveIntegerField(blank=False, null=False, default=0)
# ---------------------------------------------------------------------
# TIMESHEETS
# ---------------------------------------------------------------------

class sage_jobs(models.Model):
    job_id = models.CharField(max_length=200)
    job_desc = models.CharField(max_length=1000)

class hourly_timesheet(models.Model):
    employee_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sage_job = models.ForeignKey('sage_jobs', on_delete=models.CASCADE, null=False, blank=False)
    is_finalized = models.BooleanField(default=False, blank=False)
    hours = models.PositiveIntegerField(blank=False, null=False, default=0)
    description = models.CharField(max_length=2000, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    ts_period = (('2019-07-01 to 2019-07-14','2019-07-01 to 2019-07-14'),
                ('2019-07-15 to 2019-07-28','2019-07-15 to 2019-07-28'),
                ('2019-07-29 to 2019-08-11','2019-07-29 to 2019-08-11'),
                ('2019-08-12 to 2019-08-25','2019-08-12 to 2019-08-25'),
                ('2019-08-26 to 2019-09-08','2019-08-26 to 2019-09-08'),
                ('2019-09-09 to 2019-09-22','2019-09-09 to 2019-09-22'),
                ('2019-09-23 to 2019-10-06','2019-09-23 to 2019-10-06'),
                ('2019-10-07 to 2019-10-20','2019-10-07 to 2019-10-20'),
                ('2019-10-21 to 2019-11-03','2019-10-21 to 2019-11-03'),
                ('2019-11-04 to 2019-11-17','2019-11-04 to 2019-11-17'),
                ('2019-11-18 to 2019-12-01','2019-11-18 to 2019-12-01'),
                ('2019-12-02 to 2019-12-15','2019-12-02 to 2019-12-15'),
                ('2019-12-16 to 2019-12-29','2019-12-16 to 2019-12-29'),
                ('2019-12-30 to 2020-01-12','2019-12-30 to 2020-01-12'),
                ('2020-01-13 to 2020-01-26','2020-01-13 to 2020-01-26'),
                ('2020-01-27 to 2020-02-09','2020-01-27 to 2020-02-09'),
                ('2020-02-10 to 2020-02-23','2020-02-10 to 2020-02-23'),
                ('2020-02-24 to 2020-03-08','2020-02-24 to 2020-03-08'),
                ('2020-03-09 to 2020-03-22','2020-03-09 to 2020-03-22'),
                ('2020-03-23 to 2020-04-05','2020-03-23 to 2020-04-05'),
                ('2020-04-06 to 2020-04-19','2020-04-06 to 2020-04-19'),
                ('2020-04-20 to 2020-05-03','2020-04-20 to 2020-05-03'),
                ('2020-05-04 to 2020-05-17','2020-05-04 to 2020-05-17'),
                ('2020-05-18 to 2020-05-31','2020-05-18 to 2020-05-31'),
                ('2020-06-01 to 2020-06-14','2020-06-01 to 2020-06-14'),
                ('2020-06-15 to 2020-06-28','2020-06-15 to 2020-06-28'),
                ('2020-06-29 to 2020-07-12','2020-06-29 to 2020-07-12'),
                ('2020-07-13 to 2020-07-26','2020-07-13 to 2020-07-26'),
                ('2020-07-27 to 2020-08-09','2020-07-27 to 2020-08-09'),
                ('2020-08-10 to 2020-08-23','2020-08-10 to 2020-08-23'),
                ('2020-08-24 to 2020-09-06','2020-08-24 to 2020-09-06'),
                ('2020-09-07 to 2020-09-20','2020-09-07 to 2020-09-20'),
                ('2020-09-21 to 2020-10-04','2020-09-21 to 2020-10-04'),
                ('2020-10-05 to 2020-10-18','2020-10-05 to 2020-10-18'),
                ('2020-10-19 to 2020-11-01','2020-10-19 to 2020-11-01'),
                ('2020-11-02 to 2020-11-15','2020-11-02 to 2020-11-15'),
                ('2020-11-16 to 2020-11-29','2020-11-16 to 2020-11-29'),
                ('2020-11-30 to 2020-12-13','2020-11-30 to 2020-12-13'),
                ('2020-12-14 to 2020-12-27','2020-12-14 to 2020-12-27'),
                ('2020-12-28 to 2021-01-10','2020-12-28 to 2021-01-10'),
                ('2021-01-11 to 2021-01-24','2021-01-11 to 2021-01-24'),
                ('2021-01-25 to 2021-02-07','2021-01-25 to 2021-02-07'),
                ('2021-02-08 to 2021-02-21','2021-02-08 to 2021-02-21'),
                ('2021-02-22 to 2021-03-07','2021-02-22 to 2021-03-07'),
                ('2021-03-08 to 2021-03-21','2021-03-08 to 2021-03-21'),
                ('2021-03-22 to 2021-04-04','2021-03-22 to 2021-04-04'),
                ('2021-04-05 to 2021-04-18','2021-04-05 to 2021-04-18'),
                ('2021-04-19 to 2021-05-02','2021-04-19 to 2021-05-02'),
                ('2021-05-03 to 2021-05-16','2021-05-03 to 2021-05-16'),
                ('2021-05-17 to 2021-05-30','2021-05-17 to 2021-05-30'),
                ('2021-05-31 to 2021-06-13','2021-05-31 to 2021-06-13'),
                ('2021-06-14 to 2021-06-27','2021-06-14 to 2021-06-27'),
                ('2021-06-28 to 2021-07-11','2021-06-28 to 2021-07-11'),
                ('2021-07-12 to 2021-07-25','2021-07-12 to 2021-07-25'),
                ('2021-07-26 to 2021-08-08','2021-07-26 to 2021-08-08'),
                ('2021-08-09 to 2021-08-22','2021-08-09 to 2021-08-22'),
                ('2021-08-23 to 2021-09-05','2021-08-23 to 2021-09-05'),
                ('2021-09-06 to 2021-09-19','2021-09-06 to 2021-09-19'),
                ('2021-09-20 to 2021-10-03','2021-09-20 to 2021-10-03'),
                ('2021-10-04 to 2021-10-17','2021-10-04 to 2021-10-17'),
                ('2021-10-18 to 2021-10-31','2021-10-18 to 2021-10-31'),
                ('2021-11-01 to 2021-11-14','2021-11-01 to 2021-11-14'),
                ('2021-11-15 to 2021-11-28','2021-11-15 to 2021-11-28'),
                ('2021-11-29 to 2021-12-12','2021-11-29 to 2021-12-12'),
                ('2021-12-13 to 2021-12-26','2021-12-13 to 2021-12-26'))

# ---------------------------------------------------------------------
# PERFORMANCE REVIEW
# ---------------------------------------------------------------------

# List of all performance categories
class perf_cat(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class perf_forms(models.Model):
    upload_name = models.CharField(max_length=200, null=False, blank=False)
    upload = models.FileField(upload_to=RandomFileName('media/perf_form/'), null=False, blank=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    perf_cat = models.ForeignKey('perf_cat', on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.upload_name

class emp_perf_forms(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload_name = models.CharField(max_length=200, null=False, blank=False)
    upload = models.FileField(upload_to=RandomFileName('media/emp_perf_form/'), null=False, blank=False)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    manager_comment = models.CharField(max_length=5000, null=False, blank=False)
