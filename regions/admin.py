from django.contrib import admin
from .models import Region, City

admin.site.register(Region)
admin.site.register(City)
# Register your models here.
# python manage.py startapp core
# mkdir core/management
# mkdir core/management/commands
# touch core/management/commands/__init__.py
# touch core/management/commands/populate_regions.py
