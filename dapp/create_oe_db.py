import os
import sys
import django
from decouple import config

project_root = config("PROJECT_ROOT")
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors.settings')
django.setup()

from dapp.models import OE

with open("oelist.txt",'r') as file:
    for line in file:
        m = OE.objects.create(text=line.split("\n")[0]+': ')