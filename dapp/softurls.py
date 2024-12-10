from django.urls import path,include
from . import softviews
from django.conf import settings
from django.conf.urls.static import static

import os
import sys
import django
from decouple import config

project_root = config("PROJECT_ROOT")
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors.settings')
django.setup()

urlpatterns = [
    path("fetchselectedtheme/",softviews.fetchselectedtheme,name="fetchselectedtheme"),
    path("fetchadvicetofix/",softviews.fetchadvicetofix,name="fetchadvicetofix"),
    path("fetchdrugsbyname/<str:query>/",softviews.fetchdrugsbyname,name="fetchdrugsbyname"),
    path("fetchdrugsbygeneric/<str:query>/",softviews.fetchdrugsbygeneric,name="fetchdrugsbygeneric"),
    path("fetchdrugsbyclass/<str:query>/",softviews.fetchdrugsbyclass,name="fetchdrugsbyclass"),
    path("fetchprofile/<str:query>/",softviews.fetchprofile,name="fetchprofile"),
    path("changeprofile/<str:s>/",softviews.changeprofileinfo,name='changeprofileinfo'),
    path("validateuser/",softviews.validateuser,name="validateuser"),
    path("checkforexpirydate/",softviews.checkforexpirydate,name="checkforexpirydate"),
    path("createprescription/",softviews.createprescription,name="softcreateprescription"),
    path("fetchnotifications/",softviews.fetchnotifications,name="fetchnotifications"),
    path("fetchallprescriptions/",softviews.fetchallprescriptions,name="fetchallprescriptions"),
    path("fetchprescription/<str:s>/",softviews.fetchprescription,name="fetchprescription"),
    path("updateadvice/<str:s>/",softviews.updateadvice,name="updateadvice"),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)