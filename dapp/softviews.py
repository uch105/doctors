import os
from django.http import HttpResponse, JsonResponse,request
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.serializers import serialize
import requests
from .send_automail import send_automail
import random,string,json,time
from itertools import chain
from django.conf import settings
from django.utils import timezone
from .models import *
from decouple import config
from .bmdc import fetch_doctor_data
from .createprescription import create_pdf
import os
import sys
import django
from decouple import config

project_root = config("PROJECT_ROOT")
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors.settings')
django.setup()

from dapp.models import *

def get_userid(request):
    return request.user.id

def logged_in(request):
    return request.user.is_authenticated

def get_username(request):
    if logged_in(request):
        username = User.objects.get(id=get_userid(request)).username
    else:
        username = "None"
    return username

def is_student(request):
    username = User.objects.get(id=get_userid(request)).username
    if username[:3] == "sid":
        return True
    else:
        return False

def sub_validity_check(request):
    username = get_username(request)
    try:
        doctor = Doctor.objects.get(bmdc=username)
        s = Subscription.objects.get(doctor=doctor)
    except:
        student = Student.objects.get(sid=username)
        s = StudentSubscription.objects.get(student=student)
    return s.is_active

def generate_id(s,n):
    return str(str(s)+''.join(random.choices(string.ascii_uppercase+string.ascii_lowercase+string.digits,k=int(n))))

@csrf_exempt
def fetchdrugsbyname(request,query):
    drugs = list(Drug.objects.filter(brand__icontains=query).values())
    return JsonResponse(drugs,safe=False)

@csrf_exempt
def fetchdrugsbygeneric(request,query):
    drugs = list(Drug.objects.filter(generic__icontains=query).values())
    return JsonResponse(drugs,safe=False)

@csrf_exempt
def fetchdrugsbyclass(request,query):
    drugs = list(Drug.objects.filter(drug_class__icontains=query).values())
    return JsonResponse(drugs,safe=False)

@csrf_exempt
def validateuser(request):
    if request.method == "post" or request.method == "POST":
        username = request.POST.get("username") or request.post.get("username")
        password = request.POST.get("password") or request.post.get("password")

        #user checking
        try:
            try:
                doctor = Doctor.objects.get(bmdc=username)
                subscription = Subscription.objects.get(doctor=doctor)
                try:
                    softwareid = DoctorSoftwareID.objects.get(doctor=doctor).softwareID
                except:
                    software = DoctorSoftwareID.objects.create(doctor=doctor,softwareID=generate_id('appID',16),device='Desktop')
                    softwareid = software.softwareID
                if password == doctor.password:
                    data = {
                        'username': doctor.bmdc,
                        'expiry_date': subscription.expiry_date,
                        'softwareID': softwareid,
                        'message': 'Success',
                    }
                    return JsonResponse(data,safe=False)
                else:
                    data = {
                        'message':'Password did not match',
                    }
                    return JsonResponse(data,safe=False)
            except:
                student = Student.objects.get(sid=username)
                subscription = StudentSubscription.objects.get(student=student)
                try:
                    softwareid = StudentSoftwareID.objects.get(student=student).softwareID
                except:
                    software = StudentSoftwareID.objects.create(student=student,softwareID=generate_id('appID',16),device='Desktop')
                    softwareid = software.softwareID
                if password == student.password:
                    data = {
                        'username': student.sid,
                        'expiry_date': subscription.expiry_date,
                        'softwareID': softwareid,
                        'message': 'Success',
                    }
                    return JsonResponse(data,safe=False)
                else:
                    data = {
                        'message':'Password did not match',
                    }
                    return JsonResponse(data,safe=False)
        except Exception as e:
            return JsonResponse({'message': f'{e}',},safe=False)
        

@csrf_exempt
def fetchprofile(request,query):
    username = request.headers.get("Authorization-User-ID")
    if username[:3]=='sid':
        profile = Student.objects.get(sid=username)
    else:
        profile = Doctor.objects.get(bmdc=username)
    profile_data = json.loads(serialize('json', [profile]))[0]['fields']
    
    data = {
        'profile':profile_data,
        'image_url':'https://prescribemate.com'+profile.image.url,
    }
    return JsonResponse(data,safe=False)

@csrf_exempt
def changeprofileinfo(request,s):
    username = request.headers.get("Authorization-User-ID")
    data = json.loads(request.body)
    text = data.get("text")
    if username[:3]=='sid':
        profile = Student.objects.get(sid=username)
    else:
        profile = Doctor.objects.get(bmdc=username)
    if s=='name':
        profile.name = text
    elif s=='bname':
        profile.bname = text
    elif s=='email':
        profile.email = text
    elif s=='phone':
        profile.phone = text
    elif s=='job':
        profile.job = text
    elif s=='chamber':
        profile.chamber = text
    elif s=='password':
        profile.password = text
    elif s=='qualification':
        profile.qualification = text
    elif s=='bqualification':
        profile.bqualification = text
    else:
        profile.points += 1
    profile.save()
    return JsonResponse({'status':'Okay'},safe=False)

@csrf_exempt
def fetchnotifications(request):
    username = request.headers.get("Authorization-User-ID")
    if username[:3]=='sid':
        profile = Student.objects.get(sid=username)
        notifications = list(StudentNotification.objects.filter(student=profile).order_by('-timestamp').values())
    else:
        profile = Doctor.objects.get(bmdc=username)
        notifications = list(Notification.objects.filter(doctor=profile).order_by('-timestamp').values())
    return JsonResponse(notifications,safe=False)

def get_valueof_lines(i,lines):
    try:
        s = lines[int(i)]
    except:
        s = ''
    return str(s)

@csrf_exempt
def updateadvice(request,s):
    index = s
    username = request.headers.get("Authorization-User-ID")
    doctor = Doctor.objects.get(bmdc=username)
    data = json.loads(request.body)
    text = data.get("text")
    lines = text.split('\n')
    try:
        instance = AdviceTemplate.objects.filter(doctor=doctor)[int(index)-1]
        instance.advice1 = get_valueof_lines(0,lines)
        instance.advice2 = get_valueof_lines(1,lines)
        instance.advice3 = get_valueof_lines(2,lines)
        instance.advice4 = get_valueof_lines(3,lines)
        instance.advice5 = get_valueof_lines(4,lines)
        instance.save()
    except:
        AdviceTemplate.objects.create(
            doctor=doctor,
            index = index,
            advice1 = get_valueof_lines(0,lines),
            advice2 = get_valueof_lines(1,lines),
            advice3 = get_valueof_lines(2,lines),
            advice4 = get_valueof_lines(3,lines),
            advice5 = get_valueof_lines(4,lines),
        )
    return JsonResponse({'status':'Okay'},safe=False)

@csrf_exempt
def fetchallprescriptions(request):
    username = request.headers.get("Authorization-User-ID")
    doctor = Doctor.objects.get(bmdc=username)
    patients = list(Patient.objects.filter(doctor=doctor).order_by('-created').values())
    return JsonResponse(patients,safe=False)

@csrf_exempt
def fetchprescription(request,s):
    username = request.headers.get("Authorization-User-ID")
    doctor = Doctor.objects.get(bmdc=username)
    patient = Patient.objects.filter(doctor=doctor,pid=s)[0]
    patientdetails = PatientDetail.objects.filter(patient=patient)
    data = {
        'pid':patient.pid,
        'p_name':patient.name,
        'p_age':patient.age,
        'p_sex':patient.sex,
        'p_address':patient.address,
        'p_contact':patient.contact,
        'cc':patientdetails[0].details,
        'rf':patientdetails[1].details,
        'oe':patientdetails[2].details,
        'dx':patientdetails[3].details,
        'ix':patientdetails[4].details,
        'prestext':patientdetails[5].details,
        'pdf_path':f'media/files/prescription/{patient.pid}.pdf',
    }

    return JsonResponse(data)

def checkforexpirydate(request):
    username = request.headers.get("Authorization-User-ID")
    try:
        doctor = Doctor.objects.get(bmdc=username)
        subscription = Subscription.objects.get(doctor=doctor)
    except:
        student = Student.objects.get(sid=username)
        subscription = StudentSubscription.objects.get(student=student)

    data = {
        'expiry_date': subscription.expiry_date,
    }
    return JsonResponse(data,safe=False)

@csrf_exempt
def createprescription(request):
    username = request.headers.get("Authorization-User-ID")
    doctor = Doctor.objects.get(bmdc=username)
    fullname = request.POST.get("fullname")
    age = request.POST.get("age")
    sex = request.POST.get("sex")
    address = request.POST.get("address")
    contact = request.POST.get("contact")
    cc = request.POST.get("cc")
    rf = request.POST.get("rf")
    oe = request.POST.get("oe")
    dx = request.POST.get("dx")
    ix = request.POST.get("ix")
    prestext = request.POST.get("prestext")
    pid = request.POST.get("pid")

    uploaded_file = request.FILES.get("file")
    if uploaded_file:
        UPLOAD_DIR = 'media/files/prescription/'
        file_path = os.path.join(UPLOAD_DIR, f'{pid}.pdf')
        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
    patient = Patient(doctor=doctor,pid=pid,name=fullname,age=age,sex=sex,address=address,contact=contact,pdf=file_path)
    patient.save()

    PatientDetail.objects.create(patient=patient,symptom="Chief Complaints",details=cc)
    PatientDetail.objects.create(patient=patient,symptom="Risk Factors",details=rf)
    PatientDetail.objects.create(patient=patient,symptom="On Examination",details=oe)
    PatientDetail.objects.create(patient=patient,symptom="Diagnosis",details=dx)
    PatientDetail.objects.create(patient=patient,symptom="Investigations",details=ix)
    PatientDetail.objects.create(patient=patient,symptom="Prescriptions",details=prestext)

    return JsonResponse({
        "status": "success",
    })