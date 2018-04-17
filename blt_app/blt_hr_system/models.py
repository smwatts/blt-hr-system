# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import datetime

class certifications(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)