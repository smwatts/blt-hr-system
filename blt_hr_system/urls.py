from django.conf.urls import url
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import include
from django.urls import path

urlpatterns = [
    url(r'^$', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),

    # Pages relevant to only the admin (e.g. setting company locations)
    url(r'admin/admin.html', views.admin, name = 'admin'),
    url(r'admin/company_locations.html', views.company_locations, name='company_locations'),
    url(r'admin/add_company_info.html', views.add_company_info, name='add_company_info'),
    url(r'admin/edit_company_info/(?P<pk>[\w-]+)$', views.edit_company_info, name='edit_company_info'),
    url(r'admin/account_access.html', views.account_access, name='account_access'),
    url(r'admin/account_access_update/(?P<pk>[\w-]+)$', views.account_access_update, name='account_access_update'),

    # Pages relevant to employees (account setup, employee directoy, editing employee accounts)
    url(r'employees/signup/$', views.signup, name='signup'),
    url(r'employees/account.html', views.account, name = 'account'),
    url(r'employees/edit_employee_info/(?P<pk>[\w-]+)$', views.update_profile, name='edit_employee_info'),
    url(r'employees/employee_directory.html', views.employee_directory, name='employee_directory'),
    url(r'employees/employee_directory_edit.html', views.employee_directory_edit, name='employee_directory_edit'),
    url(r'employees/add_birth_date.html', views.add_birth_date, name = 'add_birth_date'),
    
    # Pages relevant to certifications (system managed certs, cert requests etc)
    url(r'certifications/certs.html', views.certs, name = 'certs'),
    url(r'certifications/certifications_maintained.html', views.certifications_maintained, name = 'certifications_maintained'),
    url(r'certifications/edit_system_certs/(?P<pk>[\w-]+)$', views.edit_system_certs, name = 'edit_system_certs'),
    url(r'certifications/managed_certs.html', views.managed_certs, name='managed_certs'),
    url(r'certifications/certification_request.html', views.certification_request, name = 'certification_request'),
    url(r'certifications/employee_required_certs.html', views.employee_required_certs, name = 'employee_required_certs'),
    url(r'certifications/edit_required_certs/(?P<pk>[\w-]+)$', views.edit_required_certs, name = 'edit_required_certs'),
    url(r'certifications/review_cert_requests.html', views.review_cert_requests, name = 'review_cert_requests'),
    url(r'certifications/review_cert/(?P<pk>[\w-]+)$', views.review_cert, name = 'review_cert'),

    # Pages relevant to absences (setting absence days, requests, approvals)
    url(r'absences/absence_request.html', views.absence_request, name = 'absence_request'),
    url(r'absences/upload_holidays.html', views.upload_holidays, name = 'upload_holidays'),
    url(r'absences/validate_holidays/(?P<pk>[\w-]+)$', views.validate_holidays, name = 'validate_holidays'), 
    url(r'absences/review_absence_request.html', views.review_absence_request, name = 'review_absence_request'),
    url(r'absences/company_holidays.html', views.company_holidays, name = 'company_holidays'), 
    url(r'absences/add_company_holidays.html', views.add_company_holidays, name = 'add_company_holidays'), 
    url(r'absences/edit_company_holiday/(?P<pk>[\w-]+)$', views.edit_company_holiday, name = 'edit_company_holiday'), 
    url(r'absences/employee_absences.html', views.employee_absences, name = 'employee_absences'),   
    url(r'absences/view_absence_requests.html', views.view_absence_requests, name = 'view_absence_requests'),    
    url(r'absences/approve_absence_request/(?P<pk>[\w-]+)$', views.approve_absence_request, name = 'approve_absence_request'),    

    # Pages relevant to performance reviews
    url(r'performance/performance_reviews.html', views.performance_reviews, name = 'performance_reviews'),
    url(r'performance/add_perf_forms.html', views.add_perf_forms, name = 'add_perf_forms'),
    url(r'performance/add_perf_cats.html', views.add_perf_cats, name = 'add_perf_cats'),
    url(r'performance/outstanding_perf_forms.html', views.outstanding_perf_forms, name = 'outstanding_perf_forms'),
    url(r'performance/view_perf_history.html', views.view_perf_history, name = 'view_perf_history'),
    url(r'performance/update_perf_cat/(?P<pk>[\w-]+)$', views.update_perf_cat, name = 'update_perf_cat'),
    url(r'performance/edit_emp_perf_cat/(?P<pk>[\w-]+)$', views.edit_emp_perf_cat, name = 'edit_emp_perf_cat'),
    url(r'performance/add_edit_perf_cat.html', views.add_edit_perf_cat, name = 'add_edit_perf_cat'),
    url(r'performance/manager_perf_centre.html', views.manager_perf_centre, name = 'manager_perf_centre'),
    url(r'performance/manager_perf_review/(?P<pk>[\w-]+)$', views.manager_perf_review, name = 'manager_perf_review'),
    url(r'performance/edit_perf_review/(?P<pk>[\w-]+)$', views.edit_perf_review, name = 'edit_perf_review'),

    # Pages relevant to employee training (onboarding requirements, system managed documents)
    url(r'training_docs/completed_ack_sub_docs.html', views.completed_ack_sub_docs, name = 'completed_ack_sub_docs'),
    url(r'training_docs/employee_doc_submitted.html', views.employee_doc_submitted, name = 'employee_doc_submitted'),
    url(r'training_docs/training_center.html', views.training_center, name = 'training_center'),
    url(r'training_docs/training_material.html', views.training_material, name = 'training_material'),
    url(r'training_docs/delete_training_doc.html', views.delete_training_doc, name = 'delete_training_doc'),
    url(r'training_docs/edit_onboarding_cat/(?P<pk>[\w-]+)$', views.edit_onboarding_cat, name = 'edit_onboarding_cat'),
    url(r'training_docs/onboarding_requirement.html', views.onboarding_requirement, name = 'onboarding_requirement'),
    url(r'training_docs/edit_ack_requirement/(?P<pk>[\w-]+)$', views.edit_ack_requirement, name = 'edit_ack_requirement'),
    url(r'training_docs/edit_submission_req/(?P<pk>[\w-]+)$', views.edit_submission_req, name = 'edit_submission_req'),
    url(r'training_docs/onboarding_training_docs.html', views.onboarding_training_docs, name = 'onboarding_training_docs'),
    url(r'training_docs/review_ack_docs.html', views.review_ack_docs, name = 'review_ack_docs'),
    url(r'training_docs/review_sub_docs.html', views.review_sub_docs, name = 'review_sub_docs'),
    url(r'training_docs/ack_doc_read/(?P<pk>[\w-]+)$', views.ack_doc_read, name = 'ack_doc_read'),
    url(r'training_docs/edit_doc_submission/(?P<pk>[\w-]+)$', views.edit_doc_submission, name = 'edit_doc_submission'),
    url(r'training_docs/manage_onboarding_docs.html', views.manage_onboarding_docs, name = 'manage_onboarding_docs'),
    url(r'training_docs/change_doc_status/(?P<pk>[\w-]+)$', views.change_doc_status, name = 'change_doc_status'),

    # Pages relevant to the timesheet module
    url(r'timesheet/timesheet_home.html', views.timesheet_home, name = 'timesheet_home'),
    url(r'timesheet/timesheet_selection.html', views.timesheet_selection, name = 'timesheet_selection'),
    url(r'timesheet/timesheet_center/(?P<pk>[\w-]+)$', views.timesheet_center, name = 'timesheet_center'),
    url(r'timesheet/jobs_upload.html', views.jobs_upload, name = 'jobs_upload'),
    url(r'timesheet/job_upload_edit/(?P<pk>[\w-]+)$', views.job_upload_edit, name = 'job_upload_edit'),
    url(r'timesheet/admin_timesheet_home.html', views.admin_timesheet_home, name = 'admin_timesheet_home'),
    url(r'timesheet/admin_timesheet/(?P<pk>[\w-]+)$', views.admin_timesheet, name = 'admin_timesheet'),
    url(r'timesheet/export_timesheets.html', views.export_timesheets, name = 'export_timesheets'),
    url(r'timesheet/timesheet_status.html', views.timesheet_status, name = 'timesheet_status'),
    url(r'timesheet/timesheet_hourly/(?P<pk>[\w-]+)$', views.timesheet_hourly, name = 'timesheet_hourly'),
    url(r'timesheet/timesheet_export.html', views.timesheet_export, name = 'timesheet_export'),
    url(r'timesheet/edit_timesheet_home.html', views.edit_timesheet_home, name = 'edit_timesheet_home'),
    url(r'timesheet/edit_timesheet_jobs/(?P<pk>[\w-]+)$', views.edit_timesheet_jobs, name = 'edit_timesheet_jobs'),
    url(r'timesheet/edit_timesheet_complete/(?P<pk>[\w-]+)$', views.edit_timesheet_complete, name = 'edit_timesheet_complete'),
    
]

