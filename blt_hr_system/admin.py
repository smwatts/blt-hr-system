from django.contrib import admin

from .models import (employee_group, employee_absence, employee, vaction_allocation,
	certification, company_info, holiday, cert_group, employee_certification)

admin.site.register(employee_group)
admin.site.register(employee_absence)
admin.site.register(employee)
admin.site.register(certification)
admin.site.register(company_info)
admin.site.register(holiday)
admin.site.register(cert_group)
admin.site.register(employee_certification)
admin.site.register(vaction_allocation)