from django.test import TestCase

import os
import django
from django.utils.translation import gettext as _

# Set the environment variable to point to your Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'distributorebi.settings')

# Initialize Django
django.setup()

# Now you can use translation functions
print(_("This is a test translation."))



