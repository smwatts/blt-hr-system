from django.db import models
from django.contrib.auth.models import AbstractUser

# class User(AbstractUser):
#     bio = models.TextField(max_length=500, blank=True)
#     location = models.CharField(max_length=30, blank=True)
#     birth_date = models.DateField(null=True, blank=True)

# class User(AbstractUser):
#     # contains information pretaining to each employee
#     # USERNAME_FIELD = 'email'
#     email = models.CharField(max_length=200, null=True, blank=True)
#     first_name = models.CharField(max_length=200, null=True, blank=True)
#     last_name = models.CharField(max_length=200, null=True, blank=True)
#     birth_date = models.DateField(null=True, blank=True)
#     start_date = models.DateField(null=True, blank=True)
#     employee_group = models.ForeignKey('employee_group', on_delete=models.SET_NULL, null=True)
#     # manager = models.ForeignKey(User)
#     region = models.ForeignKey('company_info', on_delete=models.SET_NULL, null=True)
#     is_active = models.BooleanField(default=False, blank=True)