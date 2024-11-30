import os
import sys
import django
from decouple import config

project_root = config("PROJECT_ROOT")
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors.settings')
django.setup()

from dapp.models import DoctorCategory

category = ['Medicine','BDS','Surgery','Gyne & Obs',]

for item in category:
    DoctorCategory.objects.get_or_create(name=item)