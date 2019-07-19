from django.contrib import admin

from .models import (employee_absence, vaction_allocation,
	certification, company_info)

admin.site.register(employee_absence)
admin.site.register(certification)
admin.site.register(company_info)
admin.site.register(vaction_allocation)