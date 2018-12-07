from django.contrib import admin

from .models import (employee_group, employee_absence, vaction_allocation,
	certification, company_info, holiday, certs_maintained)

admin.site.register(employee_group)
admin.site.register(employee_absence)
admin.site.register(certification)
admin.site.register(company_info)
admin.site.register(holiday)
admin.site.register(certs_maintained)
admin.site.register(vaction_allocation)