import os
import sys
import django

# Step 1: Add your project root to the sys.path
project_root = 'C:\\Users\\uch\\Downloads\\projects\\doctors'  # Replace this with the absolute path to your project root (where manage.py is)
sys.path.append(project_root)
# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors.settings')
django.setup()
from dapp.models import MedicalCollege

with open("collegelist.txt",'r') as file:
    for line in file:
        m = MedicalCollege.objects.create(name=line.strip())
        m.save()