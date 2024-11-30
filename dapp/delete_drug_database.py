import os
import sys
import django
from decouple import config

project_root = config("PROJECT_ROOT")
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors.settings')
django.setup()

from dapp.models import Drug

def delete_all_drug():
    drugs = Drug.objects.all()
    counter = 0
    for drug in drugs:
        drug.delete()
        counter += 1
        if counter%100==0:
            print(str(counter)+" drugs deleted")
    print("Total "+str(counter)+" drugs deleted.")

delete_all_drug()