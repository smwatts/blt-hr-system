from .absences import *
from .admin import *
from .certifications import *
from .employees import *
from .performance import *
from .registration import *
from .training_docs import *

from django.urls import reverse
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from .. import models
from .. import forms
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import datetime
import datedelta
from django.db.models import Q
from collections import defaultdict
from django.db import connection

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')