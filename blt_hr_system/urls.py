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
    url(r'employee_directory_edit.html', views.employee_directory_edit, name='employee_directory_edit'),
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