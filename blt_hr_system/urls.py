from django.conf.urls import url
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import include
from django.urls import path

urlpatterns = [
    url(r'^$', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'admin.html', views.admin, name = 'admin'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'edit_employee_info/(?P<pk>[\w-]+)$', views.update_profile, name='edit_employee_info'),
    url(r'employee_directory.html', views.employee_directory, name='employee_directory'),
    url(r'company_locations.html', views.company_locations, name='company_locations'),
     url(r'edit_company_info/(?P<pk>[\w-]+)$', views.edit_company_info, name='edit_company_info'),
    url(r'add_company_info.html', views.add_company_info, name='add_company_info'),
    url(r'managed_certs.html', views.managed_certs, name='managed_certs'),
    url(r'employee_directory_edit.html', views.employee_directory_edit, name='employee_directory_edit'),
    url(r'certification_request.html', views.certification_request, name = 'certification_request'),
    url(r'certifications.html', views.certifications, name = 'certifications'),
    url(r'absence_request.html', views.absence_request, name = 'absence_request'),
    url(r'training_center.html', views.training_center, name = 'training_center'),
    url(r'account.html', views.account, name = 'account'),
    url(r'performance_reviews.html', views.performance_reviews, name = 'performance_reviews'),
    url(r'training_material.html', views.training_material, name = 'training_material'),
    url(r'delete_training_doc.html', views.delete_training_doc, name = 'delete_training_doc'),
    url(r'add_birth_date.html', views.add_birth_date, name = 'add_birth_date'),
    url(r'employee_required_certs.html', views.employee_required_certs, name = 'employee_required_certs'),
    url(r'edit_required_certs/(?P<pk>[\w-]+)$', views.edit_required_certs, name = 'edit_required_certs'),
    url(r'edit_system_certs/(?P<pk>[\w-]+)$', views.edit_system_certs, name = 'edit_system_certs'),
    url(r'certifications_maintained.html', views.certifications_maintained, name = 'certifications_maintained'),
]

