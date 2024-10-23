import os
import sys
import django

project_root = '/var/www/doctors/'
#project_root = 'C:\\Users\\uch\\Downloads\\projects\\doctors'
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors.settings')
django.setup()

from dapp.models import MedicalCollege

with open("collegelist.txt",'r') as file:
    for line in file:
        m = MedicalCollege.objects.create(name=line.strip())
        m.save()