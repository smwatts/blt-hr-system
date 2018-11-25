from django.conf.urls import url
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'admin.html', views.admin, name = 'admin'),
    url(r'^registration/login/$', auth_views.login, name='login'),
    url(r'certification_request.html', views.certification_request, name = 'certification_request'),
    url(r'absence_request.html', views.absence_request, name = 'absence_request'),
    url(r'training_center.html', views.training_center, name = 'training_center'),
    url(r'employee_groups.html', views.employee_group, name = 'employee_group'),
    url(r'add_employee_group.html', views.add_employee_group, name = 'add_employee_group'),
    url(r'account.html', views.account, name = 'account'),
    url(r'cert_groups.html', views.cert_groups, name = 'cert_groups'),
    url(r'performance_reviews.html', views.performance_reviews, name = 'performance_reviews'),
    url(r'training_material.html', views.training_material, name = 'training_material'),
    url(r'delete_training_doc.html', views.delete_training_doc, name = 'delete_training_doc'),
]