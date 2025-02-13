from django.contrib import admin
from . import models as app_models

# Register your models here.
admin.site.register(app_models.EmployeeMetrics)
admin.site.register(app_models.Employee)