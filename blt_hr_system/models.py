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

# ---------------------------------------------------------------------
# ADMIN CONTROLS
# ---------------------------------------------------------------------
class control_options(models.Model):
    access_level = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.access_level

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
    access = models.ManyToManyField(control_options)
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
    def __str__(self):
        return self.job_id + ' - ' + self.job_desc

class hourly_timesheet(models.Model):
    employee_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sage_job = models.ForeignKey('sage_jobs', on_delete=models.CASCADE, null=False, blank=False)
    is_finalized = models.BooleanField(default=False, blank=False)
    hours = models.PositiveIntegerField(blank=False, null=False, default=0)
    description = models.CharField(max_length=2000, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    ts_period_strs = ((1,'Jul 01 2019 to Jul 14 2019'),
                (2,'Jul 15 2019 to Jul 28 2019'),
                (3,'Jul 29 2019 to Aug 11 2019'),
                (4,'Aug 12 2019 to Aug 25 2019'),
                (5,'Aug 26 2019 to Sep 08 2019'),
                (6,'Sep 09 2019 to Sep 22 2019'),
                (7,'Sep 23 2019 to Oct 06 2019'),
                (8,'Oct 07 2019 to Oct 20 2019'),
                (9,'Oct 21 2019 to Nov 03 2019'),
                (10,'Nov 04 2019 to Nov 17 2019'),
                (11,'Nov 18 2019 to Dec 01 2019'),
                (12,'Dec 02 2019 to Dec 15 2019'),
                (13,'Dec 16 2019 to Dec 29 2019'),
                (14,'Dec 30 2019 to Jan 12 2020'),
                (15,'Jan 13 2020 to Jan 26 2020'),
                (16,'Jan 27 2020 to Feb 09 2020'),
                (17,'Feb 10 2020 to Feb 23 2020'),
                (18,'Feb 24 2020 to Mar 08 2020'),
                (19,'Mar 09 2020 to Mar 22 2020'),
                (20,'Mar 23 2020 to Apr 05 2020'),
                (21,'Apr 06 2020 to Apr 19 2020'),
                (22,'Apr 20 2020 to May 03 2020'),
                (23,'May 04 2020 to May 17 2020'),
                (24,'May 18 2020 to May 31 2020'),
                (25,'Jun 01 2020 to Jun 14 2020'),
                (26,'Jun 15 2020 to Jun 28 2020'),
                (27,'Jun 29 2020 to Jul 12 2020'),
                (28,'Jul 13 2020 to Jul 26 2020'),
                (29,'Jul 27 2020 to Aug 09 2020'),
                (30,'Aug 10 2020 to Aug 23 2020'),
                (31,'Aug 24 2020 to Sep 06 2020'),
                (32,'Sep 07 2020 to Sep 20 2020'),
                (33,'Sep 21 2020 to Oct 04 2020'),
                (34,'Oct 05 2020 to Oct 18 2020'),
                (35,'Oct 19 2020 to Nov 01 2020'),
                (36,'Nov 02 2020 to Nov 15 2020'),
                (37,'Nov 16 2020 to Nov 29 2020'),
                (38,'Nov 30 2020 to Dec 13 2020'),
                (39,'Dec 14 2020 to Dec 27 2020'),
                (40,'Dec 28 2020 to Jan 10 2021'),
                (41,'Jan 11 2021 to Jan 24 2021'),
                (42,'Jan 25 2021 to Feb 07 2021'),
                (43,'Feb 08 2021 to Feb 21 2021'),
                (44,'Feb 22 2021 to Mar 07 2021'),
                (45,'Mar 08 2021 to Mar 21 2021'),
                (46,'Mar 22 2021 to Apr 04 2021'),
                (47,'Apr 05 2021 to Apr 18 2021'),
                (48,'Apr 19 2021 to May 02 2021'),
                (49,'May 03 2021 to May 16 2021'),
                (50,'May 17 2021 to May 30 2021'),
                (51,'May 31 2021 to Jun 13 2021'),
                (52,'Jun 14 2021 to Jun 27 2021'),
                (53,'Jun 28 2021 to Jul 11 2021'),
                (54,'Jul 12 2021 to Jul 25 2021'),
                (55,'Jul 26 2021 to Aug 08 2021'),
                (56,'Aug 09 2021 to Aug 22 2021'),
                (57,'Aug 23 2021 to Sep 05 2021'),
                (58,'Sep 06 2021 to Sep 19 2021'),
                (59,'Sep 20 2021 to Oct 03 2021'),
                (60,'Oct 04 2021 to Oct 17 2021'),
                (61,'Oct 18 2021 to Oct 31 2021'),
                (62,'Nov 01 2021 to Nov 14 2021'),
                (63,'Nov 15 2021 to Nov 28 2021'),
                (64,'Nov 29 2021 to Dec 12 2021'),
                (65,'Dec 13 2021 to Dec 26 2021'))
    ts_period = models.CharField(max_length=200, choices=ts_period_strs, null=True)

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
    employee = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField(upload_to=RandomFileName('media/emp_perf_form/'), null=False, blank=False)
    upload_name = models.CharField(max_length=200, null=False, blank=False)
    manager_upload = models.FileField(upload_to=RandomFileName('media/emp_manager_perf_form/'), 
        null=True, blank=True)
    manager_upload_name = models.CharField(max_length=200, null=True, blank=True)
    manager_uploaded_at = models.DateTimeField(null=True)
    year_opts = ((2019,2019),
                (2020,2020),
                (2021,2021),
                (2022,2022),
                (2023,2023),
                (2024,2024))
    year = models.PositiveIntegerField(choices=year_opts, null=True)

