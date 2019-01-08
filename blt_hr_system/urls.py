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
    url(r'review_cert_requests.html', views.review_cert_requests, name = 'review_cert_requests'),
    url(r'review_cert/(?P<pk>[\w-]+)$', views.review_cert, name = 'review_cert'),
    url(r'manage_onboarding_docs.html', views.manage_onboarding_docs, name = 'manage_onboarding_docs'),
    url(r'edit_onboarding_docs/(?P<pk>[\w-]+)$', views.edit_onboarding_docs, name = 'edit_onboarding_docs'),
    url(r'onboarding_requirement.html', views.onboarding_requirement, name = 'onboarding_requirement'),
    url(r'edit_ack_requirement/(?P<pk>[\w-]+)$', views.edit_ack_requirement, name = 'edit_ack_requirement'),
    url(r'edit_submission_req/(?P<pk>[\w-]+)$', views.edit_submission_req, name = 'edit_submission_req'),
    url(r'onboarding_training_docs.html', views.onboarding_training_docs, name = 'onboarding_training_docs'),
    url(r'ack_doc_read/(?P<pk>[\w-]+)$', views.ack_doc_read, name = 'ack_doc_read'),
]

