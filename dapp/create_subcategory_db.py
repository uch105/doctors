import os
import sys
import django
from decouple import config

project_root = config("PROJECT_ROOT")
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors.settings')
django.setup()

from dapp.models import DoctorSubCategory,DoctorCategory

with open("subcategory.txt",'r') as file:
    for line in file:
        DoctorSubCategory.objects.get_or_create(category=DoctorCategory.objects.get(name=line.split('-')[0]),name=line.split('-')[1].strip())