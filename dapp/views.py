from django.http import HttpResponse, JsonResponse,request
from django.core.serializers import serialize
from django.shortcuts import render,redirect
from django.contrib.auth import login as auth_login
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from requests import request
import requests
import datetime
import os
from .send_automail import send_automail
import random,string,json,time
from itertools import chain
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.timezone import now
from .models import *
from decouple import config
from .bmdc import fetch_doctor_data
from .createprescription import create_pdf







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

def catergory_conversion(s):
    d = {
        'MBBS':'এমবিবিএস',
        'BDS':'বিডিএস',
    }
    return d[str(s)]

def sub_category_conversion(s):
    d = {
        'Burn & Plastic':'বার্ন এন্ড প্লাস্টিক সার্জারি',
        'Hepatology':'হেপাটোলজি',
        'Nephrology':'নেফ্রোলজি',
        'Cardiology':'কার্ডিওলজি',
        'Endocrynology':'এন্ডোক্রাইনোলজি',
        'Neuro Medicine':'নিউরো মেডিসিন',
        'Physical Medicine':'ফিজিক্যাল মেডিসিন',
        'Urology':'ইউরোলজি',
        'Hematology':'হেমাটোলজি',
        'Gastroenterology':'গ্যাস্ট্রোএন্টারোলজি',
        'ENT':'ইএনটি',
        'Cardiothorasic':'কার্ডিওথোরাসিক',
        'Respiratory Medicine':'রেসপিরেটরি মেডিসিন',
        'Dermatology':'ডার্মাটোলজি',
        'Orthopedics':'অর্থোপেডিক',
        'Eye':'চোখ',
        'Pediatrics Medicine':'পেডিয়াট্রিকস মেডিসিন',
        'Pediatrics Surgery':'পেডিয়াট্রিকস সার্জারি',
        'Neuro Surgery':'নিউরো সার্জারি',
        'Radiology':'রেডিওলজি',
        'Oncology':'অনকোলজি',
        'Colorectal':'কলোরেক্টাল',
        'Obstetrics':'গাইনি এন্ড অবস',
        'General BDS':'জেনারেল বিডিএস',
        'General Medicine':'জেনারেল মেডিসিন',
    }
    return d[str(s)]






def home(request):
    return render(request,"dapp/index.html")

def terms(request):
    return render(request,"dapp/terms.html")

def privacy(request):
    return render(request,"dapp/privacy.html")

def about(request):
    return render(request,"dapp/about.html")













def login(request):
    if request.method == "POST":
        username = request.POST.get("bmdc")
        password = request.POST.get("password")
        try:
            try:
                doctor = Doctor.objects.get(bmdc=username)
                if password == doctor.password:
                    user = User.objects.get(username=username)
                    auth_login(request,user)
                    return redirect("forum")
                else:
                    cats = DoctorCategory.objects.all()
                    subcats = DoctorSubCategory.objects.all()
                    context = {
                        'cats': cats,
                        'subcats': subcats,
                        'message': 'Password did not match!',
                    }
                    return render(request,"dapp/login.html",context)
            except:
                student = Student.objects.get(sid=username)
                if password == student.password:
                    user = User.objects.get(username=username)
                    auth_login(request,user)
                    return redirect("forum")
                else:
                    cats = DoctorCategory.objects.all()
                    subcats = DoctorSubCategory.objects.all()
                    context = {
                        'cats': cats,
                        'subcats': subcats,
                        'message': 'Password did not match!',
                    }
                    return render(request,"dapp/login.html",context)
        except:
            cats = DoctorCategory.objects.all()
            subcats = DoctorSubCategory.objects.all()
            context = {
                'cats': cats,
                'subcats': subcats,
                'message': 'User not found!',
            }
            return render(request,"dapp/login.html",context)
    cats = DoctorCategory.objects.all()
    subcats = DoctorSubCategory.objects.all()
    context = {
        'cats': cats,
        'subcats': subcats,
    }
    return render(request,"dapp/login.html",context)

def log_out(request):
    logout(request)
    return redirect('login')

def additional(request,pk):
    if request.method == "POST":
        doctors = []
        try:
            doctor = Doctor.objects.filter(email=request.POST.get("email"))
            doctors += doctor
        except:
            doctor = Doctor.objects.filter(phone=request.POST.get("phone"))
            doctors += doctor
        if len(doctors) == 0:
            doctor = Doctor.objects.get(bmdc=pk)
            doctor.phone = request.POST.get("phone")
            doctor.email = request.POST.get("email")
            doctor.gender = request.POST.get("gender")
            doctor.job = request.POST.get("job")
            doctor.chamber = request.POST.get("chamber")
            doctor.image = request.FILES["image"]
            doctor.password = request.POST.get("password")
            doctor.save()
            send_automail(to_email=doctor.email,subject="Welcome to Prescribemate - Your Account is Ready!",body=f"Hi {doctor.name},\n\n We're excited to inform you that your Prescribemate account has been successfully created! You can now log in and begin exploring.\n\nUsername : {pk}\nPassword : {doctor.password}\n\nThank you for choosing Prescribemate. We're here to ensure you have the best experience possible. If you need any assistance, don't hesitate to reach out.\n\n\nBest regards,\nTeam Prescribemate")
            user = User.objects.create(username=pk,password=doctor.password,email=doctor.email)
            auth_login(request,user)
            return redirect("forum")
        else:
            return redirect('additional',pk,{"bmdc":pk,"message":"Email/phone has already been used before!"})
    context = {
        'bmdc': pk,
    }
    return render(request,"dapp/additional.html",context)

def signin(request):
    bmdc = request.POST.get("bmdc")
    c = request.POST.get("category")
    sc = request.POST.get("subcategory")
    sub_category = DoctorSubCategory.objects.get(name=sc)
    category = sub_category.category
    link = request.POST.get("link")
    context = fetch_doctor_data(link)
    if context['Validation']:
        try:
            instance = Doctor.objects.get(bmdc=c+bmdc)
            cats = DoctorCategory.objects.all()
            subcats = DoctorSubCategory.objects.all()
            context = {
                'cats': cats,
                'subcats': subcats,
                'message': "Profile already exist! If it is not you, please contact immediately",
            }
            return render(request,'dapp/login.html',context)
        except:
            instance = Doctor.objects.create(bmdc=c+bmdc,category=category,sub_category=sub_category,bsub_category=sub_category_conversion(sub_category),name=context['name'],reg_year=context['regyear'],valid_till=context['regvalidyear'],blood_group=context['bg'],status= True,dob=context['dob'],fname=context['fname'],mname=context['mname'])
            instance.save()
            s = Subscription.objects.create(doctor=instance,is_active=True)
            n = Notification.objects.create(doctor=instance,text="Welcome to prescribemate! Thank you for choosing us.",link="#")
            s.save()
            n.save()
            return redirect("additional",pk=c+bmdc)
    else:
        cats = DoctorCategory.objects.all()
        subcats = DoctorSubCategory.objects.all()
        context = {
            'cats': cats,
            'subcats': subcats,
            'message': "Invalid profile link! Please check again.",
        }
        return render(request,"dapp/login.html",context)

def studentsignin(request):
    if request.method == "POST":
        try:
            try:
                student = Student.objects.get(phone=request.POST.get("phone"))
                clgs = MedicalCollege.objects.all()
                context = {
                    'clgs': clgs,
                    'message': "Phone number already exist!",
                }
                return render(request,"dapp/studentsignin.html",context)
            except:
                student = Student.objects.get(email=request.POST.get("email"))
                clgs = MedicalCollege.objects.all()
                context = {
                    'clgs': clgs,
                    'message': "Email already registered!",
                }
                return render(request,"dapp/studentsignin.html",context)
        except:
            student = Student.objects.create(sid=generate_id("sid",5),name=request.POST.get("name"),phone=request.POST.get("phone"),email=request.POST.get("email"),dob=request.POST.get("dob"),gender=request.POST.get("gender"),blood_group=request.POST.get("blood_group"),institute=MedicalCollege.objects.get(name=request.POST.get("institute")),password=request.POST.get("password"),image=request.FILES["image"])
            student.save()
            user = User.objects.create(username=student.sid,password=student.password)
            user.save()
            send_automail(to_email=student.email,subject="Welcome to Prescribemate - Your Account is Ready!",body=f"Hi {student.name},\n\n We're excited to inform you that your Prescribemate account has been successfully created! You can now log in and begin exploring.\n\nUsername : {student.sid}\nPassword : {student.password}\n\nThank you for choosing Prescribemate. We're here to ensure you have the best experience possible. If you need any assistance, don't hesitate to reach out.\n\nBest regards,\nTeam Prescribemate")
            instance1 = StudentSubscription.objects.create(student=student,is_active=True)
            instance2 = StudentNotification.objects.create(student=student,text="Welcome to prescribemate! Thank you for choosing us.",link="#")
            instance1.save()
            instance2.save()
            cats = DoctorCategory.objects.all()
            subcats = DoctorSubCategory.objects.all()
            context = {
                'cats': cats,
                'subcats': subcats,
                'message': f"Account creation successful! Username and password has been sent to {student.email}. Please check (also spam email)",
            }
            return render(request,"dapp/login.html",context)
    clgs = MedicalCollege.objects.all()
    context = {
        'clgs': clgs,
    }
    return render(request,"dapp/studentsignin.html",context)

def studentlogin(request):
    return render(request,"dapp/studentlogin.html")

def studentreset(request):
    if request.method == "POST":
        try:
            try:
                email = request.POST.get("email")
                student = Student.objects.get(email=email)
                send_automail(to_email=student.email,subject="Prescribemate - Account Recovery Request",body=f"Hi {student.name},\n\nWe have successfully restored your account password. You can now log in using the details provided below:\n\nUsername: {student.sid}\nPassword: {student.password}\n\nPlease make sure to keep your login details secure, and don't hesitate to contact us if you need any further assistance.\n\nThank you for choosing Prescribemate! We're committed to providing you with a seamless user experience.\n\nBest regards,\nTeam Prescribemate")
                context = {
                    'message': f"An email has been sent to {email}. Please check and login again.",
                }
                return render(request,"dapp/studentreset.html",context)
            except:
                context = {
                    'message': "Given email is not registered",
                }
                return render(request,"dapp/studentreset.html",context)
        except:
            try:
                phone = request.POST.get("phone")
                student = Student.objects.get(phone=phone)
                send_automail(to_email=student.email,subject="Prescribemate - Account Recovery Request",body=f"Hi {student.name},\n\nWe have successfully restored your account password. You can now log in using the details provided below:\n\nUsername: {student.sid}\nPassword: {student.password}\n\nPlease make sure to keep your login details secure, and don't hesitate to contact us if you need any further assistance.\n\nThank you for choosing Prescribemate! We're committed to providing you with a seamless user experience.\n\nBest regards,\nTeam Prescribemate")
                context = {
                    'message': f"An email has been sent to {email}. Please check and login again.",
                }
                return render(request,"dapp/studentreset.html",context)
            except:
                context = {
                    'message': "Given phone number is not registered",
                }
                return render(request,"dapp/studentreset.html",context)
    context = {}
    return render(request,"dapp/studentreset.html",context)

@require_POST
def reportlogin(request):
    ReportLogin.objects.create(bmdc="Login",text=request.POST.get("report"))
    return redirect('home',{'message':'Report has been submitted! Please have patience.'})

def reset(request):
    bmdc = request.POST.get("bmdc")
    c = request.POST.get("category")
    doctor = Doctor.objects.get(bmdc=c+bmdc)
    send_automail(to_email=doctor.email,subject="Prescribemate - Account Recovery Request",body=f"Hi {doctor.name},\n\nWe have successfully restored your account password. You can now log in using the details provided below:\n\nUsername: {doctor.bmdc}\nPassword: {doctor.password}\n\nPlease make sure to keep your login details secure, and don't hesitate to contact us if you need any further assistance.\n\nThank you for choosing Prescribemate! We're committed to providing you with a seamless user experience.\n\nBest regards,\nTeam Prescribemate")
    context = {
        'message': f'An email has been sent to {doctor.email}. Please check spam folder also!'
    }
    return render(request,"dapp/login.html",context)




















@login_required(login_url="/log-in/")
def dashboard_prescription(request):
    doctor = Doctor.objects.get(bmdc=get_username(request))
    if request.GET.get("filter")=="yesterday":
        current_time = now()
        yesterday_start = (current_time - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = (current_time - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        patients = Patient.objects.filter(created__range=(yesterday_start, yesterday_end)).order_by('-created')
        context={
            'filter_value': 'yesterday',
            'doctor': doctor,
            'sub_valid': Subscription.objects.get(doctor=doctor).is_active,
            'patients': patients,
        }
    elif request.GET.get("filter")=="last_week":
        current_time = now()
        last_week_start = (current_time - timedelta(days=current_time.weekday() + 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        last_week_end = last_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        patients = Patient.objects.filter(created__range=(last_week_start, last_week_end)).order_by('-created')
        context={
            'filter_value': 'last_week',
            'doctor': doctor,
            'sub_valid': Subscription.objects.get(doctor=doctor).is_active,
            'patients': patients,
        }
    elif request.GET.get("filter")=="last_month":
        current_time = now()
        first_day_of_current_month = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_end = first_day_of_current_month - timedelta(seconds=1)
        last_month_start = last_month_end.replace(day=1)
        patients = Patient.objects.filter(created__range=(last_month_start, last_month_end)).order_by('-created')
        context={
            'filter_value': 'last_month',
            'doctor': doctor,
            'sub_valid': Subscription.objects.get(doctor=doctor).is_active,
            'patients': patients,
        }
    elif request.GET.get("filter")=="all":
        patients = Patient.objects.all().order_by('-created')
        context={
            'filter_value': 'all',
            'doctor': doctor,
            'sub_valid': Subscription.objects.get(doctor=doctor).is_active,
            'patients': patients,
        }
    else:
        patients = Patient.objects.filter(doctor=doctor).order_by('-created')[:20]
    context={
        'doctor': doctor,
        'sub_valid': Subscription.objects.get(doctor=doctor).is_active,
        'patients': patients,
    }
    return render(request,"dapp/dashboard-prescription.html",context)

@login_required(login_url="/log-in/")
def dashboard_createprescription(request):
    doctor = Doctor.objects.get(bmdc=get_username(request))
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        age = request.POST.get("age")
        sex = request.POST.get("sex")
        address = request.POST.get("address")
        occupation = request.POST.get("occupation")
        contact = request.POST.get("contact")
        cc = request.POST.get("cc")
        oe = request.POST.get("oe")
        dx = request.POST.get("dx")
        ix = request.POST.get("ix")
        prestext = request.POST.get("prestext")

        text_blocks = [
            {"text": 'C/C: '+cc+"\n\n"+"O/E: "+oe, "x": 83.333, "y": 1400.8333, "width": 2062.5, "height": 500},
            {"text": 'Ix: '+ix, "x": 83.333, "y": 2170.333, "width": 2062.5, "height": 430},
            {"text": 'Dx: '+dx, "x": 83.333, "y": 2800.533, "width": 2062.5, "height": 470},
            {"text": prestext, "x": 1291.6, "y": 1156.25, "width": 2083.33333, "height": 1000},
        ]

        pid = generate_id('patient','12')

        template_image_path = config("TEMPLATE_IMAGE_PATH")
        output_pdf_path = config("OUTPUT_PDF_PATH")+f'{pid}.pdf'

        create_pdf(template_image_path=template_image_path,output_pdf_path=output_pdf_path,text_blocks=text_blocks,chamber="Chamber: "+doctor.chamber,dr_name_e=doctor.name,dr_c_e=doctor.sub_category.name,dr_q_e=doctor.qualification,dr_name_b=doctor.bname,dr_c_b=doctor.bsub_category,dr_q_b=doctor.bqualification,p_name="Name: "+fullname,p_age="Age: "+age,p_sex="Sex: "+sex,p_contact="Contact: "+contact)

        with open(output_pdf_path,'rb') as pdf_file:
            patient = Patient(doctor=doctor,pid=pid,name=fullname,age=age,sex=sex,address=address,contact=contact,occupation=occupation,pdf=f"files/prescription/{pid}.pdf")
            patient.save()
        
        PatientDetail.objects.create(patient=patient,symptom="C/C",details=request.POST.get("cc"))
        PatientDetail.objects.create(patient=patient,symptom="O/E",details=request.POST.get("oe"))
        PatientDetail.objects.create(patient=patient,symptom="Ix",details=request.POST.get("ix"))
        PatientDetail.objects.create(patient=patient,symptom="Dx",details=request.POST.get("dx"))
        PatientDetail.objects.create(patient=patient,symptom="Onset",details=request.POST.get("onset"))
        PatientDetail.objects.create(patient=patient,symptom="Onset Duration",details=request.POST.get("onset_duration"))
        PatientDetail.objects.create(patient=patient,symptom="Frequency",details=request.POST.get("onset_frequency"))
        PatientDetail.objects.create(patient=patient,symptom="Aggravating Factors",details=request.POST.get("aggravating_factors"))
        PatientDetail.objects.create(patient=patient,symptom="Relieving Factors",details=request.POST.get("relieving_factors"))
        PatientDetail.objects.create(patient=patient,symptom="Hepatobiliary Conditions",details=request.POST.get("hepatobiliary_conditions"))
        PatientDetail.objects.create(patient=patient,symptom="Drug history",details=request.POST.get("past_medications"))
        PatientDetail.objects.create(patient=patient,symptom="Past Surgeries",details=request.POST.get("past_surgeries"))
        PatientDetail.objects.create(patient=patient,symptom="Recreational Drugs",details=request.POST.get("recreational_drugs"))
        PatientDetail.objects.create(patient=patient,symptom="Edema Location",details=request.POST.get("edema_location"))
        PatientDetail.objects.create(patient=patient,symptom="Edema timing",details=request.POST.get("edema_timing"))
        PatientDetail.objects.create(patient=patient,symptom="General Appearance",details=request.POST.get("general_appearance"))
        PatientDetail.objects.create(patient=patient,symptom="Overall health status",details=request.POST.get("overall_health"))
        PatientDetail.objects.create(patient=patient,symptom="Vital Signs",details=request.POST.get("vital_signs"))
        PatientDetail.objects.create(patient=patient,symptom="BP",details=request.POST.get("blood_pressure"))
        PatientDetail.objects.create(patient=patient,symptom="Pulse",details=request.POST.get("pulse"))
        PatientDetail.objects.create(patient=patient,symptom="R/R",details=request.POST.get("respiratory_rate"))
        PatientDetail.objects.create(patient=patient,symptom="SPO2",details=request.POST.get("spo2"))
        PatientDetail.objects.create(patient=patient,symptom="Temperature",details=request.POST.get("body_temp"))
        PatientDetail.objects.create(patient=patient,symptom="Body Mass Index (BMI)",details=request.POST.get("bmi"))
        PatientDetail.objects.create(patient=patient,symptom="Any other symptoms or findings",details=request.POST.get("other_sg"))
        PatientDetail.objects.create(patient=patient,symptom="Jaundice",details='Yes' if request.POST.get("jaundice")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Abdominal Pain",details='Yes' if request.POST.get("abdominal_pain")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Nausea",details='Yes' if request.POST.get("nausea")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Change in stool color",details='Yes' if request.POST.get("change_stool_color")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Change in urine color",details='Yes' if request.POST.get("change_urine_color")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Prurities (itching)",details='Yes' if request.POST.get("itching")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Loss of appetite",details='Yes' if request.POST.get("loss_of_appetite")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Weight loss",details='Yes' if request.POST.get("weight_loss")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Fever",details='Yes' if request.POST.get("fever")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Chronic Illness",details='Yes' if request.POST.get("chronic_illness")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Diabetes",details='Yes' if request.POST.get("diabetes")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Cardiovascular Disease",details='Yes' if request.POST.get("cardiovascular_disease")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Allergies",details='Yes' if request.POST.get("allergies")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Genetic Disorders",details='Yes' if request.POST.get("genetic_disorders")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Kidney Diseases",details='Yes' if request.POST.get("kidney_disease")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Hypertension",details='Yes' if request.POST.get("hypertension")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Heart Disease",details='Yes' if request.POST.get("heart_disease")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Arthritis",details='Yes' if request.POST.get("arthritis")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Osteoporesis",details='Yes' if request.POST.get("osteoporesis")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Leukemia",details='Yes' if request.POST.get("leukemia")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Lymphoma",details='Yes' if request.POST.get("lymphoma")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Epilepsy",details='Yes' if request.POST.get("epilepsy")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Asthma",details='Yes' if request.POST.get("asthma")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Lung Disease",details='Yes' if request.POST.get("lung_disease")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Colorectal Disease",details='Yes' if request.POST.get("colorectal_disease")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Acne",details='Yes' if request.POST.get("acne")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Psoriasis",details='Yes' if request.POST.get("psoriasis")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Eczema",details='Yes' if request.POST.get("eczema")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Polyps",details='Yes' if request.POST.get("polyps")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Migraines",details='Yes' if request.POST.get("migraines")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Smoking",details='Yes' if request.POST.get("smoking")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Alcohol",details='Yes' if request.POST.get("alcohol")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Sleep Disorder",details='Yes' if request.POST.get("sleep_disorder")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Weight gain",details='Yes' if request.POST.get("weight_gain")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Fatigue",details='Yes' if request.POST.get("fatigue")=='on' else 'No')
        PatientDetail.objects.create(patient=patient,symptom="Chest Pain",details='Yes' if request.POST.get("chest_pain")=='on' else 'No')

        if "Burn & Plastic" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Location and extent of burns",details=request.POST.get("burn_location_extent"))
            PatientDetail.objects.create(patient=patient,symptom="Depth of burns",details=request.POST.get("burn_depth"))
            PatientDetail.objects.create(patient=patient,symptom="Blisters?",details='Yes' if request.POST.get("blisters")=='on' else 'No')
            PatientDetail.objects.create(patient=patient,symptom="Eschar?",details='Yes' if request.POST.get("eschar")=='on' else 'No')
            PatientDetail.objects.create(patient=patient,symptom="Necrosis?",details='Yes' if request.POST.get("necrosis")=='on' else 'No')
            PatientDetail.objects.create(patient=patient,symptom="Redness?",details='Yes' if request.POST.get("redness")=='on' else 'No')
            PatientDetail.objects.create(patient=patient,symptom="Swelling?",details='Yes' if request.POST.get("swelling")=='on' else 'No')
            PatientDetail.objects.create(patient=patient,symptom="Discharge?",details='Yes' if request.POST.get("discharge")=='on' else 'No')
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("tenderness"))
            PatientDetail.objects.create(patient=patient,symptom="Texture",details=request.POST.get("texture"))
            PatientDetail.objects.create(patient=patient,symptom="Surgical scars",details=request.POST.get("surgical_scars"))
            PatientDetail.objects.create(patient=patient,symptom="Symmetry and contour",details=request.POST.get("symmetry_contour"))
            PatientDetail.objects.create(patient=patient,symptom="Sign of infections",details=request.POST.get("sign_of_infection"))
            PatientDetail.objects.create(patient=patient,symptom="Palpation : Tenderness",details=request.POST.get("palpation_tenderness"))
            PatientDetail.objects.create(patient=patient,symptom="Palpation : Masses",details=request.POST.get("palpation_masses"))
            PatientDetail.objects.create(patient=patient,symptom="Palpation : Abnormalities",details=request.POST.get("palpation_abnormalities"))
            PatientDetail.objects.create(patient=patient,symptom="Electrolytes",details=request.POST.get("electrolytes"))
            PatientDetail.objects.create(patient=patient,symptom="Wound cultures (if infection)",details=request.POST.get("wound_cultures"))
            PatientDetail.objects.create(patient=patient,symptom="Coagulation profile",details=request.POST.get("coagulation_profile"))
            if request.FILES.get("cbc"):
                PatientDetail.objects.create(patient=patient,symptom="Complete Blood Count (CBC)",file=request.FILES.get("cbc"))
            if request.FILES.get("x-ray"):
                PatientDetail.objects.create(patient=patient,symptom="X-ray (if underlying injury is suspected)",file=request.FILES.get("x-ray"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound",file=request.FILES.get("ultrasound"))
            if request.FILES.get("mri/ctscan"):
                PatientDetail.objects.create(patient=patient,symptom="MRI/CT Scan (for complex cases)",file=request.FILES.get("mri/ctscan"))
        
        if "Hepatology" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("tenderness"))
            PatientDetail.objects.create(patient=patient,symptom="Liver size",details=request.POST.get("liver_size"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal Distension?",details='Yes' if request.POST.get("abdominal_distension")=='on' else 'No')
            PatientDetail.objects.create(patient=patient,symptom="Gallbladder Tenderness",details=request.POST.get("gallbladder_tenderness"))
            PatientDetail.objects.create(patient=patient,symptom="Spleen size",details=request.POST.get("spleen_size"))
            PatientDetail.objects.create(patient=patient,symptom="Upper border liver dullness",details=request.POST.get("border_liver_dullness"))
            PatientDetail.objects.create(patient=patient,symptom="Serum Albumin",details=request.POST.get("serum_albumin"))
            PatientDetail.objects.create(patient=patient,symptom="Prothrombin time",details=request.POST.get("prothrombin"))
            PatientDetail.objects.create(patient=patient,symptom="Ascites",details=request.POST.get("ascites"))
            PatientDetail.objects.create(patient=patient,symptom="Bowel sounds",details=request.POST.get("bowel_sounds"))
            if request.FILES.get("cbc"):
                PatientDetail.objects.create(patient=patient,symptom="Complete Blood Count (CBC)",file=request.FILES.get("cbc"))
            if request.FILES.get("hepatitis_panel"):
                PatientDetail.objects.create(patient=patient,symptom="Hepatitis panel",file=request.FILES.get("hepatitis_panel"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound of Abdomen",file=request.FILES.get("ultrasound"))
            if request.FILES.get("ctscan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan of Abdomen",file=request.FILES.get("ctscan"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI of Abdomen",file=request.FILES.get("mri"))
            if request.FILES.get("ercp"):
                PatientDetail.objects.create(patient=patient,symptom="ERCP (Endoscopic Retrograde Cholangiopancreatography)",file=request.FILES.get("ercp"))
            if request.FILES.get("liver_biopsy"):
                PatientDetail.objects.create(patient=patient,symptom="Liver biopsy",file=request.FILES.get("liver_biopsy"))
            if request.FILES.get("fibroscan"):
                PatientDetail.objects.create(patient=patient,symptom="FibroScan (Liver Fibrosis Assessment)",file=request.FILES.get("fibroscan"))
        
        if "Nephrology" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Edema extent",details=request.POST.get("edema_extent"))
            PatientDetail.objects.create(patient=patient,symptom="Skin change",details=request.POST.get("skin_change"))
            PatientDetail.objects.create(patient=patient,symptom="Palpation : Tenderness",details=request.POST.get("palpation_tenderness"))
            PatientDetail.objects.create(patient=patient,symptom="Palpation : Masses",details=request.POST.get("palpation_masses"))
            PatientDetail.objects.create(patient=patient,symptom="Bruits (Renal Arteries)",details=request.POST.get("bruits"))
            PatientDetail.objects.create(patient=patient,symptom="Heart sounds",details=request.POST.get("heart_sounds"))
            PatientDetail.objects.create(patient=patient,symptom="Peripheral pulses",details=request.POST.get("peripheral_pulses"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal examinations",details=request.POST.get("abdominal_examinations"))
            PatientDetail.objects.create(patient=patient,symptom="Serum Creatinine",details=request.POST.get("serum_creatinine"))
            PatientDetail.objects.create(patient=patient,symptom="BUN (Renal function test)",details=request.POST.get("bun"))
            PatientDetail.objects.create(patient=patient,symptom="Electrolytes",details=request.POST.get("electrolytes"))
            PatientDetail.objects.create(patient=patient,symptom="Urinalysis",details=request.POST.get("urinalysis"))
            PatientDetail.objects.create(patient=patient,symptom="Urine protein/creatinine ratio",details=request.POST.get("protein-creatinine"))
            PatientDetail.objects.create(patient=patient,symptom="GFR score",details=request.POST.get("gfr_score"))
            if request.FILES.get("cbc"):
                PatientDetail.objects.create(patient=patient,symptom="Complete Blood Count (CBC)",file=request.FILES.get("cbc"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound of Abdomen",file=request.FILES.get("ultrasound"))
            if request.FILES.get("ctscan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan of Abdomen",file=request.FILES.get("ctscan"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI of Abdomen",file=request.FILES.get("mri"))
            if request.FILES.get("renal_biopsy"):
                PatientDetail.objects.create(patient=patient,symptom="Renal biopsy",file=request.FILES.get("renal_biopsy"))
        
        if "Cardiology" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Apex beat",details=request.POST.get("apex_beat"))
            PatientDetail.objects.create(patient=patient,symptom="Palpable P2",details=request.POST.get("palpablep2"))
            PatientDetail.objects.create(patient=patient,symptom="Peripheral Pulse Quality",details=request.POST.get("peripheral_pulse_quality"))
            PatientDetail.objects.create(patient=patient,symptom="Peripheral Pulse Symmetry",details=request.POST.get("peripheral_pulse_symmetry"))
            PatientDetail.objects.create(patient=patient,symptom="Heart sound (s1)",details=request.POST.get("heart_sound_s1"))
            PatientDetail.objects.create(patient=patient,symptom="Heart sound (s2)",details=request.POST.get("heart_sound_s2"))
            PatientDetail.objects.create(patient=patient,symptom="(Additional)",details=request.POST.get("heart_sound_additional"))
            PatientDetail.objects.create(patient=patient,symptom="Murmurs type",details=request.POST.get("murmurs_type"))
            PatientDetail.objects.create(patient=patient,symptom="Murmurs location",details=request.POST.get("murmurs_location"))
            PatientDetail.objects.create(patient=patient,symptom="Murmurs intensity",details=request.POST.get("murmurs_intensity"))
            PatientDetail.objects.create(patient=patient,symptom="Electrolytes",details=request.POST.get("electrolytes"))
            PatientDetail.objects.create(patient=patient,symptom="Lipid profile",details=request.POST.get("lipid_profile"))
            PatientDetail.objects.create(patient=patient,symptom="BUN (Renal function test)",details=request.POST.get("bun"))
            PatientDetail.objects.create(patient=patient,symptom="Cardiac Biomarkers (Troponins)",details=request.POST.get("cardiac_biomarker"))
            PatientDetail.objects.create(patient=patient,symptom="Holter Monitor (24h ECG)",details=request.POST.get("holter_monitor"))
            if request.FILES.get("cbc"):
                PatientDetail.objects.create(patient=patient,symptom="Complete Blood Count (CBC)",file=request.FILES.get("cbc"))
            if request.FILES.get("ecg"):
                PatientDetail.objects.create(patient=patient,symptom="ECG",file=request.FILES.get("ecg"))
            if request.FILES.get("xray"):
                PatientDetail.objects.create(patient=patient,symptom="Chest X-Ray",file=request.FILES.get("xray"))
            if request.FILES.get("ecocardiogram"):
                PatientDetail.objects.create(patient=patient,symptom="Ecocardiogram",file=request.FILES.get("ecocardiogram"))
            
        if "Endocrynology" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Thyroid size",details=request.POST.get("thyroid_size"))
            PatientDetail.objects.create(patient=patient,symptom="Consistency",details=request.POST.get("thyroid_consistency"))
            PatientDetail.objects.create(patient=patient,symptom="Nodules",details=request.POST.get("thyroid_nodules"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("thyroid_tenderness"))
            PatientDetail.objects.create(patient=patient,symptom="Skin Texture",details=request.POST.get("skin_texture"))
            PatientDetail.objects.create(patient=patient,symptom="Pigmentation",details=request.POST.get("skin_pigmentation"))
            PatientDetail.objects.create(patient=patient,symptom="Sweating",details=request.POST.get("skin_sweating"))
            PatientDetail.objects.create(patient=patient,symptom="Hands (Tremors)",details=request.POST.get("hands_tremors"))
            PatientDetail.objects.create(patient=patient,symptom="(Palmar Erythema)",details=request.POST.get("hands_palmar_erythema"))
            PatientDetail.objects.create(patient=patient,symptom="Jugular venous pressure",details=request.POST.get("neck_jugular_venous_pressure"))
            PatientDetail.objects.create(patient=patient,symptom="Lymphadenopathy",details=request.POST.get("neck_lymphadenopathy"))
            PatientDetail.objects.create(patient=patient,symptom="Organomegaly",details=request.POST.get("abdomen_organomegaly"))
            PatientDetail.objects.create(patient=patient,symptom="Striae",details=request.POST.get("abdomen_striae"))
            PatientDetail.objects.create(patient=patient,symptom="Edema",details=request.POST.get("lower_limbs_edema"))
            PatientDetail.objects.create(patient=patient,symptom="Reflexes",details=request.POST.get("lower_limbs_reflexes"))
            PatientDetail.objects.create(patient=patient,symptom="Blood glucose levels",details=request.POST.get("blood_glucose_levels"))
            PatientDetail.objects.create(patient=patient,symptom="HbA1c",details=request.POST.get("hba1c"))
            PatientDetail.objects.create(patient=patient,symptom="Thyroid (T3)",details=request.POST.get("thyroid_t3"))
            PatientDetail.objects.create(patient=patient,symptom="Thyroid (T4)",details=request.POST.get("thyroid_t4"))
            PatientDetail.objects.create(patient=patient,symptom="Thyroid (TSH)",details=request.POST.get("thyroid_tsh"))
            PatientDetail.objects.create(patient=patient,symptom="Cortisol levels",details=request.POST.get("cortisol_levels"))
            PatientDetail.objects.create(patient=patient,symptom="Electrolytes",details=request.POST.get("electrolytes"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound",file=request.FILES.get("ultrasound"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan / MRI",file=request.FILES.get("ct_scan"))
        
        if "Neuro Medicine" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient, symptom="Short/Long term memory", details=request.POST.get("mental_memory"))
            PatientDetail.objects.create(patient=patient, symptom="Attention", details=request.POST.get("mental_attention"))
            PatientDetail.objects.create(patient=patient, symptom="Function & Sensory Assessment", details=request.POST.get("cranial_nerves"))
            PatientDetail.objects.create(patient=patient, symptom="Muscle strength", details=request.POST.get("motor_system_1"))
            PatientDetail.objects.create(patient=patient, symptom="Tone", details=request.POST.get("motor_system_2"))
            PatientDetail.objects.create(patient=patient, symptom="Co-ordination", details=request.POST.get("motor_system_3"))
            PatientDetail.objects.create(patient=patient, symptom="Light touch", details=request.POST.get("sensory_1"))
            PatientDetail.objects.create(patient=patient, symptom="Pain touch", details=request.POST.get("sensory_2"))
            PatientDetail.objects.create(patient=patient, symptom="Temperature sense", details=request.POST.get("sensory_3"))
            PatientDetail.objects.create(patient=patient, symptom="Vibration sense", details=request.POST.get("sensory_4"))
            PatientDetail.objects.create(patient=patient, symptom="Proprioception sense", details=request.POST.get("sensory_5"))
            PatientDetail.objects.create(patient=patient, symptom="Deep tendon reflexes", details=request.POST.get("reflexes_1"))
            PatientDetail.objects.create(patient=patient, symptom="Pathological reflexes", details=request.POST.get("reflexes_2"))
            PatientDetail.objects.create(patient=patient, symptom="Walking pattern", details=request.POST.get("gait_balance_1"))
            PatientDetail.objects.create(patient=patient, symptom="Balance tests", details=request.POST.get("gait_balance_2"))
            PatientDetail.objects.create(patient=patient, symptom="Electrolytes", details=request.POST.get("electrolytes"))
            PatientDetail.objects.create(patient=patient, symptom="Thyroid (T3)", details=request.POST.get("thyroid_t3"))
            PatientDetail.objects.create(patient=patient, symptom="Thyroid (T4)", details=request.POST.get("thyroid_t4"))
            PatientDetail.objects.create(patient=patient, symptom="Thyroid (TSH)", details=request.POST.get("thyroid_tsh"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient, symptom="CT Scan (Head)", file=request.FILES.get("ct_scan"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient, symptom="MRI (Brain)", file=request.FILES.get("mri"))
            if request.FILES.get("eeg"):
                PatientDetail.objects.create(patient=patient, symptom="EEG", file=request.FILES.get("eeg"))
            if request.FILES.get("lumbar_puncture"):
                PatientDetail.objects.create(patient=patient, symptom="Lumbar puncture", file=request.FILES.get("lumbar_puncture"))
            if request.FILES.get("evoked"):
                PatientDetail.objects.create(patient=patient, symptom="Evoked potentials", file=request.FILES.get("evoked"))
            if request.FILES.get("genetictest"):
                PatientDetail.objects.create(patient=patient, symptom="Genetic testing", file=request.FILES.get("genetictest"))
        
        if "Physical Medicine" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Joint deformities",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Muscle atrophy",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Swelling",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Temp. Cahnge",details=request.POST.get("palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Active range of motion",details=request.POST.get("rom_1"))
            PatientDetail.objects.create(patient=patient,symptom="Passive range of motion",details=request.POST.get("rom_2"))
            PatientDetail.objects.create(patient=patient,symptom="Muscle groups (grade strength)",details=request.POST.get("strength"))
            PatientDetail.objects.create(patient=patient,symptom="Muscle strength",details=request.POST.get("motor_system_1"))
            PatientDetail.objects.create(patient=patient,symptom="Tone",details=request.POST.get("motor_system_2"))
            PatientDetail.objects.create(patient=patient,symptom="Co-ordination",details=request.POST.get("motor_system_3"))
            PatientDetail.objects.create(patient=patient,symptom="Light touch",details=request.POST.get("sensory_1"))
            PatientDetail.objects.create(patient=patient,symptom="Pain touch",details=request.POST.get("sensory_2"))
            PatientDetail.objects.create(patient=patient,symptom="Temperature sense",details=request.POST.get("sensory_3"))
            PatientDetail.objects.create(patient=patient,symptom="Vibration sense",details=request.POST.get("sensory_4"))
            PatientDetail.objects.create(patient=patient,symptom="Proprioception sense",details=request.POST.get("sensory_5"))
            PatientDetail.objects.create(patient=patient,symptom="Deep tendon reflexes",details=request.POST.get("reflexes_1"))
            PatientDetail.objects.create(patient=patient,symptom="Pathological reflexes",details=request.POST.get("reflexes_2"))
            PatientDetail.objects.create(patient=patient,symptom="Electrolytes",details=request.POST.get("electrolytes"))
            PatientDetail.objects.create(patient=patient,symptom="Thyroid (T3)",details=request.POST.get("thyroid_t3"))
            PatientDetail.objects.create(patient=patient,symptom="Thyroid (T4)",details=request.POST.get("thyroid_t4"))
            PatientDetail.objects.create(patient=patient,symptom="Thyroid (TSH)",details=request.POST.get("thyroid_tsh"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI",file=request.FILES.get("mri"))
            if request.FILES.get("emg"):
                PatientDetail.objects.create(patient=patient,symptom="EMG",file=request.FILES.get("emg"))

        if "Urology" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Abdominal distension",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="External genitalia",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal Tenderness",details=request.POST.get("palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Testicular examination",details=request.POST.get("palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Kidney tenderness",details=request.POST.get("percussion"))
            PatientDetail.objects.create(patient=patient,symptom="Bowel sounds",details=request.POST.get("auscultation"))
            PatientDetail.objects.create(patient=patient,symptom="Electrolytes",details=request.POST.get("electrolytes"))
            PatientDetail.objects.create(patient=patient,symptom="Serum creatinine",details=request.POST.get("serum_creatinine"))
            PatientDetail.objects.create(patient=patient,symptom="Urine RME",details=request.POST.get("urinalysis"))
            PatientDetail.objects.create(patient=patient,symptom="Urine culture",details=request.POST.get("urine_culture"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan (Abdomen)",file=request.FILES.get("ct_scan"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI (Pelvis)",file=request.FILES.get("mri"))
            if request.FILES.get("cystoscopy"):
                PatientDetail.objects.create(patient=patient,symptom="Cystoscopy",file=request.FILES.get("cystoscopy"))
            if request.FILES.get("urodynamics"):
                PatientDetail.objects.create(patient=patient,symptom="Urodynamics",file=request.FILES.get("urodynamics"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound of pelvis/abdomen",file=request.FILES.get("ultrasound"))

        if "Hematology" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Pallor",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Bruises or Petechiae",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Swollen lymph nodes",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness in bone area",details=request.POST.get("palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Splenomegaly or Hepatomegaly",details=request.POST.get("palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Heart sounds",details=request.POST.get("auscultation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Lung sounds",details=request.POST.get("auscultation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Reticulocyte counts",details=request.POST.get("reticulocyte"))
            PatientDetail.objects.create(patient=patient,symptom="Coagulation profile",details=request.POST.get("coagulation"))
            PatientDetail.objects.create(patient=patient,symptom="Vitamin B12 & Folate levels",details=request.POST.get("vitamin"))
            PatientDetail.objects.create(patient=patient,symptom="Bone marrow biopsy",details=request.POST.get("bone_marrow"))
            PatientDetail.objects.create(patient=patient,symptom="Serum Iron Studies",details=request.POST.get("serum_iron"))
            PatientDetail.objects.create(patient=patient,symptom="LDH",details=request.POST.get("ldh"))
            PatientDetail.objects.create(patient=patient,symptom="Peripheral blood semar",details=request.POST.get("pbf"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound (Abdomen)",file=request.FILES.get("ultrasound"))
        
        if "Gastroenterology" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Distension",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Scars",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Skin changes",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Masses",details=request.POST.get("palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Liver size",details=request.POST.get("palpation_3"))
            PatientDetail.objects.create(patient=patient,symptom="Spleen size",details=request.POST.get("palpation_4"))
            PatientDetail.objects.create(patient=patient,symptom="Upper border dullness",details=request.POST.get("percussion_1"))
            PatientDetail.objects.create(patient=patient,symptom="Ascites",details=request.POST.get("percussion_2"))
            PatientDetail.objects.create(patient=patient,symptom="Bowel sounds",details=request.POST.get("auscultation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Bruits",details=request.POST.get("auscultation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Liver function test",details=request.POST.get("lft"))
            PatientDetail.objects.create(patient=patient,symptom="Renal function test",details=request.POST.get("rft"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Stool analysis",details=request.POST.get("stool"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan (Abdomen)",file=request.FILES.get("ct_scan"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound (Abdomen)",file=request.FILES.get("ultrasound"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI (Abdomen)",file=request.FILES.get("mri"))
            if request.FILES.get("upper_endoscopy"):
                PatientDetail.objects.create(patient=patient,symptom="Upper endoscopy",file=request.FILES.get("upper_endoscopy"))
            if request.FILES.get("colonoscopy"):
                PatientDetail.objects.create(patient=patient,symptom="Colonoscopy",file=request.FILES.get("colonoscopy"))
            if request.FILES.get("flexible_sigmoidoscopy"):
                PatientDetail.objects.create(patient=patient,symptom="Flexible sigmoidoscopy",file=request.FILES.get("flexible_sigmoidoscopy"))
            
        if "ENT" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="External ear",details=request.POST.get("ear_inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Ear canal",details=request.POST.get("ear_inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Tympanic membrane",details=request.POST.get("ear_inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Ear tenderness (Auricle)",details=request.POST.get("ear_palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Ear tenderness (Mastoid)",details=request.POST.get("ear_palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="External nose",details=request.POST.get("nose_inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Nasal cavity",details=request.POST.get("nose_inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Sinus tenderness (frontal)",details=request.POST.get("nose_palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Sinus tenderness (maxillary)",details=request.POST.get("nose_palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Oral cavity",details=request.POST.get("throat_inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Pharynx",details=request.POST.get("throat_inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Tonsils",details=request.POST.get("throat_inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Lymph nodes (cervical)",details=request.POST.get("throat_palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Lymph nodes (submandibular)",details=request.POST.get("throat_palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Alergy testing",details=request.POST.get("alergy"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan (Sinuses)",file=request.FILES.get("ct_scan"))
            if request.FILES.get("x-ray"):
                PatientDetail.objects.create(patient=patient,symptom="X-Ray (Sinuses)",file=request.FILES.get("x-ray"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI (Head-Neck)",file=request.FILES.get("mri"))
            if request.FILES.get("nasal_endoscopy"):
                PatientDetail.objects.create(patient=patient,symptom="Nasal endoscopy",file=request.FILES.get("nasal_endoscopy"))
            if request.FILES.get("laryngoscopy"):
                PatientDetail.objects.create(patient=patient,symptom="Laryngoscopy",file=request.FILES.get("laryngoscopy"))
            if request.FILES.get("audiometry"):
                PatientDetail.objects.create(patient=patient,symptom="Audiometry",file=request.FILES.get("audiometry"))

        if "Cardiothorasic" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Chest deformities or scars",details=request.POST.get("cardiac_inspection"))
            PatientDetail.objects.create(patient=patient,symptom="Herat size & location",details=request.POST.get("cardiac_palpation"))
            PatientDetail.objects.create(patient=patient,symptom="Herat sound",details=request.POST.get("cardiac_auscultation"))
            PatientDetail.objects.create(patient=patient,symptom="Respiratory rate",details=request.POST.get("thorasic_inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Respiratory pattern",details=request.POST.get("thorasic_inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Chest wall movement",details=request.POST.get("thorasic_inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("thorasic_palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Chest expansion",details=request.POST.get("thorasic_palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Dullness or hyperresonance",details=request.POST.get("thorasic_auscultation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Breath sounds",details=request.POST.get("thorasic_auscultation_2"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Basic metabolic panel",details=request.POST.get("basic_metabolic_panel"))
            PatientDetail.objects.create(patient=patient,symptom="Cardiac enzymes",details=request.POST.get("cardiac_enzymes"))
            PatientDetail.objects.create(patient=patient,symptom="Arterial blood gas",details=request.POST.get("abg"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan (Chest)",file=request.FILES.get("ct_scan"))
            if request.FILES.get("x-ray"):
                PatientDetail.objects.create(patient=patient,symptom="X-Ray (Chest)",file=request.FILES.get("x-ray"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI (Chest)",file=request.FILES.get("mri"))
            if request.FILES.get("cardiac_stress_test"):
                PatientDetail.objects.create(patient=patient,symptom="Cardiac stress test",file=request.FILES.get("cardiac_stress_test"))
            if request.FILES.get("pulmonary_function"):
                PatientDetail.objects.create(patient=patient,symptom="Pulmonary function",file=request.FILES.get("pulmonary_function"))
            if request.FILES.get("coronary_angiography"):
                PatientDetail.objects.create(patient=patient,symptom="Coronary Angiography",file=request.FILES.get("coronary_angiography"))

        if "Dermatology" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Skin lesions",details=request.POST.get("dermatological_inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Hair & Nail examination",details=request.POST.get("dermatological_inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Texture",details=request.POST.get("dermatological_palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("dermatological_palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Temp. Changes",details=request.POST.get("dermatological_palpation_3"))
            PatientDetail.objects.create(patient=patient,symptom="Genital lesions",details=request.POST.get("genitourinary_inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Discharge",details=request.POST.get("genitourinary_inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("genitourinary_palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Lymphadenopathy",details=request.POST.get("genitourinary_palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Dullness or hyperresonance",details=request.POST.get("thorasic_auscultation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Breath sounds",details=request.POST.get("thorasic_auscultation_2"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Skin scrapings",details=request.POST.get("skin_scraping"))
            PatientDetail.objects.create(patient=patient,symptom="STDs (HIV,Syphilis,Gonorrhea)",details=request.POST.get("std"))
            PatientDetail.objects.create(patient=patient,symptom="Urinalysis",details=request.POST.get("urinalysis"))
            PatientDetail.objects.create(patient=patient,symptom="STI panel",details=request.POST.get("sti_panel"))

        if "Orthopedics" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Swelling",details=request.POST.get("orthopedic_inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Deformities",details=request.POST.get("orthopedic_inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Scars",details=request.POST.get("orthopedic_inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Redness",details=request.POST.get("orthopedic_inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("orthopedic_palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Warmth",details=request.POST.get("orthopedic_palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Crepitus",details=request.POST.get("orthopedic_palpation_3"))
            PatientDetail.objects.create(patient=patient,symptom="Masses",details=request.POST.get("orthopedic_palpation_4"))
            PatientDetail.objects.create(patient=patient,symptom="Active range of motion",details=request.POST.get("orthopedic_rom_1"))
            PatientDetail.objects.create(patient=patient,symptom="Passive range of motion",details=request.POST.get("orthopedic_rom_2"))
            PatientDetail.objects.create(patient=patient,symptom="Gait analysis: Normal?",details=request.POST.get("orthopedic_gait_1"))
            PatientDetail.objects.create(patient=patient,symptom="Antalgic",details=request.POST.get("orthopedic_gait_2"))
            PatientDetail.objects.create(patient=patient,symptom="Strength Test (Grade 0-5)",details=request.POST.get("orthopedic_strength_1"))
            PatientDetail.objects.create(patient=patient,symptom="Stability",details=request.POST.get("orthopedic_strength_2"))
            PatientDetail.objects.create(patient=patient,symptom="Light touch",details=request.POST.get("sensory_1"))
            PatientDetail.objects.create(patient=patient,symptom="Pain touch",details=request.POST.get("sensory_2"))
            PatientDetail.objects.create(patient=patient,symptom="Vibration sense",details=request.POST.get("sensory_3"))
            PatientDetail.objects.create(patient=patient,symptom="Proprioception",details=request.POST.get("sensory_4"))
            PatientDetail.objects.create(patient=patient,symptom="Deep tendon reflexes",details=request.POST.get("reflex_1"))
            PatientDetail.objects.create(patient=patient,symptom="Pathological reflexes",details=request.POST.get("reflex_2"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="ESR",details=request.POST.get("esr"))
            PatientDetail.objects.create(patient=patient,symptom="CRP",details=request.POST.get("crp"))
            PatientDetail.objects.create(patient=patient,symptom="Rheumatoid Factor (RF)",details=request.POST.get("rf"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT Scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("x-ray"):
                PatientDetail.objects.create(patient=patient,symptom="X-Ray",file=request.FILES.get("x-ray"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI",file=request.FILES.get("mri"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound",file=request.FILES.get("ultrasound"))
            if request.FILES.get("bone_scan"):
                PatientDetail.objects.create(patient=patient,symptom="Bone scan",file=request.FILES.get("bone_scan"))

        if "Eye" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Distant vision(Snellen chart)",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Near vision(Joeger chart)",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Eyelids",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Conjunctiva",details=request.POST.get("inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Sclera",details=request.POST.get("inspection_5"))
            PatientDetail.objects.create(patient=patient,symptom="Refraction",details=request.POST.get("inspection_6"))
            PatientDetail.objects.create(patient=patient,symptom="Pupil size",details=request.POST.get("inspection_7"))
            PatientDetail.objects.create(patient=patient,symptom="Pupil Shape",details=request.POST.get("inspection_8"))
            PatientDetail.objects.create(patient=patient,symptom="Reactivity to light",details=request.POST.get("inspection_9"))
            PatientDetail.objects.create(patient=patient,symptom="Extraocular movements",details=request.POST.get("inspection_10"))
            PatientDetail.objects.create(patient=patient,symptom="Alignment (cover test)",details=request.POST.get("inspection_11"))
            PatientDetail.objects.create(patient=patient,symptom="Cornea",details=request.POST.get("inspection_12"))
            PatientDetail.objects.create(patient=patient,symptom="Anterior chamber",details=request.POST.get("inspection_13"))
            PatientDetail.objects.create(patient=patient,symptom="Iris",details=request.POST.get("inspection_14"))
            PatientDetail.objects.create(patient=patient,symptom="Lens",details=request.POST.get("inspection_15"))
            PatientDetail.objects.create(patient=patient,symptom="Tonometry",details=request.POST.get("inspection_16"))
            PatientDetail.objects.create(patient=patient,symptom="Fundoscopy (Optic disc, macula)",details=request.POST.get("inspection_17"))
            PatientDetail.objects.create(patient=patient,symptom="Blood glucose levels",details=request.POST.get("blood_glucose"))
            PatientDetail.objects.create(patient=patient,symptom="Thyroid function test",details=request.POST.get("thyroid_function"))
            PatientDetail.objects.create(patient=patient,symptom="Intraocular pressure measurement",details=request.POST.get("intraocular_pressure"))
            if request.FILES.get("oct"):
                PatientDetail.objects.create(patient=patient,symptom="OCT",file=request.FILES.get("oct"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound B-scan",file=request.FILES.get("ultrasound"))
            if request.FILES.get("fluorescein_angiography"):
                PatientDetail.objects.create(patient=patient,symptom="Fluorescein Angiography",file=request.FILES.get("fluorescein_angiography"))

        if "Pediatrics Medicine" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Frontanelles",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Eye movements",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Ear examination",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Throat examination",details=request.POST.get("inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Heart sounds",details=request.POST.get("inspection_5"))
            PatientDetail.objects.create(patient=patient,symptom="Murmurs",details=request.POST.get("inspection_6"))
            PatientDetail.objects.create(patient=patient,symptom="Breath sounds",details=request.POST.get("inspection_7"))
            PatientDetail.objects.create(patient=patient,symptom="Wheezes",details=request.POST.get("inspection_8"))
            PatientDetail.objects.create(patient=patient,symptom="Crackles",details=request.POST.get("inspection_9"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal inspection",details=request.POST.get("inspection_10"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal palpation",details=request.POST.get("inspection_11"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal percussion",details=request.POST.get("inspection_12"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal auscultation",details=request.POST.get("inspection_13"))
            PatientDetail.objects.create(patient=patient,symptom="External genitalia",details=request.POST.get("inspection_14"))
            PatientDetail.objects.create(patient=patient,symptom="Hernias",details=request.POST.get("inspection_15"))
            PatientDetail.objects.create(patient=patient,symptom="Limb exam.",details=request.POST.get("inspection_16"))
            PatientDetail.objects.create(patient=patient,symptom="Joint exam.",details=request.POST.get("inspection_17"))
            PatientDetail.objects.create(patient=patient,symptom="Spine exam.",details=request.POST.get("inspection_18"))
            PatientDetail.objects.create(patient=patient,symptom="Reflexes",details=request.POST.get("inspection_19"))
            PatientDetail.objects.create(patient=patient,symptom="Muscle tone",details=request.POST.get("inspection_20"))
            PatientDetail.objects.create(patient=patient,symptom="Sensory",details=request.POST.get("inspection_21"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Electrolytes",details=request.POST.get("electrolytes"))
            PatientDetail.objects.create(patient=patient,symptom="Liver function test",details=request.POST.get("lft"))
            PatientDetail.objects.create(patient=patient,symptom="Urinalysis",details=request.POST.get("urinalysis"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound",file=request.FILES.get("ultrasound"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI",file=request.FILES.get("mri"))
            if request.FILES.get("xray"):
                PatientDetail.objects.create(patient=patient,symptom="X-Ray",file=request.FILES.get("xray"))

        if "Pediatrics Surgery" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Frontanelles",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Eye movements",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Ear examination",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Throat examination",details=request.POST.get("inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Heart sounds",details=request.POST.get("inspection_5"))
            PatientDetail.objects.create(patient=patient,symptom="Murmurs",details=request.POST.get("inspection_6"))
            PatientDetail.objects.create(patient=patient,symptom="Breath sounds",details=request.POST.get("inspection_7"))
            PatientDetail.objects.create(patient=patient,symptom="Wheezes",details=request.POST.get("inspection_8"))
            PatientDetail.objects.create(patient=patient,symptom="Crackles",details=request.POST.get("inspection_9"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal inspection",details=request.POST.get("inspection_10"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal palpation",details=request.POST.get("inspection_11"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal percussion",details=request.POST.get("inspection_12"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal auscultation",details=request.POST.get("inspection_13"))
            PatientDetail.objects.create(patient=patient,symptom="External genitalia",details=request.POST.get("inspection_14"))
            PatientDetail.objects.create(patient=patient,symptom="Hernias",details=request.POST.get("inspection_15"))
            PatientDetail.objects.create(patient=patient,symptom="Limb exam.",details=request.POST.get("inspection_16"))
            PatientDetail.objects.create(patient=patient,symptom="Joint exam.",details=request.POST.get("inspection_17"))
            PatientDetail.objects.create(patient=patient,symptom="Spine exam.",details=request.POST.get("inspection_18"))
            PatientDetail.objects.create(patient=patient,symptom="Reflexes",details=request.POST.get("inspection_19"))
            PatientDetail.objects.create(patient=patient,symptom="Muscle tone",details=request.POST.get("inspection_20"))
            PatientDetail.objects.create(patient=patient,symptom="Sensory",details=request.POST.get("inspection_21"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Electrolytes",details=request.POST.get("electrolytes"))
            PatientDetail.objects.create(patient=patient,symptom="Liver function test",details=request.POST.get("lft"))
            PatientDetail.objects.create(patient=patient,symptom="Urinalysis",details=request.POST.get("urinalysis"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound",file=request.FILES.get("ultrasound"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI",file=request.FILES.get("mri"))
            if request.FILES.get("xray"):
                PatientDetail.objects.create(patient=patient,symptom="X-Ray",file=request.FILES.get("xray"))

        if "Neuro Surgery" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Mental orientation",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Memory",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Speech",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Cognition",details=request.POST.get("inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Olfaction",details=request.POST.get("inspection_5"))
            PatientDetail.objects.create(patient=patient,symptom="Vision",details=request.POST.get("inspection_6"))
            PatientDetail.objects.create(patient=patient,symptom="Eye movement",details=request.POST.get("inspection_7"))
            PatientDetail.objects.create(patient=patient,symptom="Facial Sensation",details=request.POST.get("inspection_8"))
            PatientDetail.objects.create(patient=patient,symptom="Hearing & balance",details=request.POST.get("inspection_9"))
            PatientDetail.objects.create(patient=patient,symptom="Shoulder shrug",details=request.POST.get("inspection_10"))
            PatientDetail.objects.create(patient=patient,symptom="Tongue movements",details=request.POST.get("inspection_11"))
            PatientDetail.objects.create(patient=patient,symptom="Muscle bulk",details=request.POST.get("inspection_12"))
            PatientDetail.objects.create(patient=patient,symptom="Co-ordination",details=request.POST.get("inspection_13"))
            PatientDetail.objects.create(patient=patient,symptom="Strength",details=request.POST.get("inspection_14"))
            PatientDetail.objects.create(patient=patient,symptom="Light touch",details=request.POST.get("inspection_15"))
            PatientDetail.objects.create(patient=patient,symptom="Pain touch",details=request.POST.get("inspection_16"))
            PatientDetail.objects.create(patient=patient,symptom="Vibration",details=request.POST.get("inspection_17"))
            PatientDetail.objects.create(patient=patient,symptom="Proprioception",details=request.POST.get("inspection_18"))
            PatientDetail.objects.create(patient=patient,symptom="Deep tendon reflexes",details=request.POST.get("inspection_19"))
            PatientDetail.objects.create(patient=patient,symptom="Plantar response",details=request.POST.get("inspection_20"))
            PatientDetail.objects.create(patient=patient,symptom="Walking pattern",details=request.POST.get("inspection_21"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Electrolytes",details=request.POST.get("electrolytes"))
            PatientDetail.objects.create(patient=patient,symptom="Coagulation profile",details=request.POST.get("coagulation"))
            PatientDetail.objects.create(patient=patient,symptom="Urinalysis",details=request.POST.get("urinalysis"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("angiography"):
                PatientDetail.objects.create(patient=patient,symptom="Angiography",file=request.FILES.get("angiography"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI",file=request.FILES.get("mri"))
            if request.FILES.get("eeg"):
                PatientDetail.objects.create(patient=patient,symptom="EEG",file=request.FILES.get("eeg"))

        if "Radiology" in doctor.sub_category.name:
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound",file=request.FILES.get("ultrasound"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI",file=request.FILES.get("mri"))
            if request.FILES.get("xray"):
                PatientDetail.objects.create(patient=patient,symptom="X-Ray",file=request.FILES.get("xray"))
            if request.FILES.get("mammography"):
                PatientDetail.objects.create(patient=patient,symptom="Mammography",file=request.FILES.get("mammography"))
            if request.FILES.get("nuclear_medicine"):
                PatientDetail.objects.create(patient=patient,symptom="Nuclear Medicine Studies",file=request.FILES.get("nuclear_medicine"))
            if request.FILES.get("body_part"):
                PatientDetail.objects.create(patient=patient,symptom="Body part exam.",file=request.FILES.get("body_part"))

        if "Oncology" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Visible tumors",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Swelling",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness location",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness Size",details=request.POST.get("inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Lymphadenopathy location",details=request.POST.get("inspection_5"))
            PatientDetail.objects.create(patient=patient,symptom="Lymphadenopathy size",details=request.POST.get("inspection_6"))
            PatientDetail.objects.create(patient=patient,symptom="Lymphadenopathy consistency",details=request.POST.get("inspection_7"))
            PatientDetail.objects.create(patient=patient,symptom="Abnormal sounds in areas",details=request.POST.get("inspection_8"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Tumor markers",details=request.POST.get("tumor_marker"))
            PatientDetail.objects.create(patient=patient,symptom="Liver function test",details=request.POST.get("lft"))
            PatientDetail.objects.create(patient=patient,symptom="Renal function test",details=request.POST.get("rft"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound",file=request.FILES.get("ultrasound"))
            if request.FILES.get("mri"):
                PatientDetail.objects.create(patient=patient,symptom="MRI",file=request.FILES.get("mri"))
            if request.FILES.get("biopsy"):
                PatientDetail.objects.create(patient=patient,symptom="Biopsy",file=request.FILES.get("biopsy"))
            if request.FILES.get("pet_scan"):
                PatientDetail.objects.create(patient=patient,symptom="PET Scan",file=request.FILES.get("pet_scan"))
            if request.FILES.get("molecular_test"):
                PatientDetail.objects.create(patient=patient,symptom="Molecular Testing",file=request.FILES.get("molecular_test"))

        if "Colorectal" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Distension",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Scars",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Visible peristalsis",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("palpation_1"))
            PatientDetail.objects.create(patient=patient,symptom="Masses",details=request.POST.get("palpation_2"))
            PatientDetail.objects.create(patient=patient,symptom="Organomegaly",details=request.POST.get("palpation_3"))
            PatientDetail.objects.create(patient=patient,symptom="Tympany",details=request.POST.get("percussion_1"))
            PatientDetail.objects.create(patient=patient,symptom="Dullness",details=request.POST.get("percussion_2"))
            PatientDetail.objects.create(patient=patient,symptom="Bowel sounds",details=request.POST.get("percussion_3"))
            PatientDetail.objects.create(patient=patient,symptom="Hemorrhoids",details=request.POST.get("inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Fissures",details=request.POST.get("inspection_5"))
            PatientDetail.objects.create(patient=patient,symptom="Fistulas",details=request.POST.get("inspection_6"))
            PatientDetail.objects.create(patient=patient,symptom="DRE: masses",details=request.POST.get("dre_1"))
            PatientDetail.objects.create(patient=patient,symptom="DRE: tenderness",details=request.POST.get("dre_2"))
            PatientDetail.objects.create(patient=patient,symptom="DRE: Sphincter tone",details=request.POST.get("dre_3"))
            PatientDetail.objects.create(patient=patient,symptom="DRE: Blood on gloves",details=request.POST.get("dre_4"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Liver function test",details=request.POST.get("lft"))
            PatientDetail.objects.create(patient=patient,symptom="Fecal Occult Blood test",details=request.POST.get("fobt"))
            PatientDetail.objects.create(patient=patient,symptom="CRP",details=request.POST.get("crp"))
            PatientDetail.objects.create(patient=patient,symptom="Tumor markers",details=request.POST.get("tumor_marker"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound (Abdominal)",file=request.FILES.get("ultrasound"))
            if request.FILES.get("colonoscopy"):
                PatientDetail.objects.create(patient=patient,symptom="Colonoscopy",file=request.FILES.get("colonoscopy"))

        if "Obstetrics" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="External genitalia",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Signs of infections",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal tenderness",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Uterine tenderness",details=request.POST.get("inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Uterine size",details=request.POST.get("inspection_5"))
            PatientDetail.objects.create(patient=patient,symptom="Ovarian masses",details=request.POST.get("inspection_6"))
            PatientDetail.objects.create(patient=patient,symptom="Vaginal Walls",details=request.POST.get("inspection_7"))
            PatientDetail.objects.create(patient=patient,symptom="Cervix",details=request.POST.get("inspection_8"))
            PatientDetail.objects.create(patient=patient,symptom="Ovarian size",details=request.POST.get("inspection_9"))
            PatientDetail.objects.create(patient=patient,symptom="Ovarian tenderness",details=request.POST.get("inspection_10"))
            PatientDetail.objects.create(patient=patient,symptom="Sign of swelling/edema",details=request.POST.get("inspection_11"))
            PatientDetail.objects.create(patient=patient,symptom="Fundal height",details=request.POST.get("inspection_12"))
            PatientDetail.objects.create(patient=patient,symptom="Fetal heart tone",details=request.POST.get("inspection_13"))
            PatientDetail.objects.create(patient=patient,symptom="Abdominal Girth",details=request.POST.get("inspection_14"))
            PatientDetail.objects.create(patient=patient,symptom="Cervical dilation",details=request.POST.get("inspection_15"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Urinalysis",details=request.POST.get("urinalysis"))
            PatientDetail.objects.create(patient=patient,symptom="Pregnancy test",details=request.POST.get("pregnancy"))
            PatientDetail.objects.create(patient=patient,symptom="Pap smear",details=request.POST.get("pap_semar"))
            PatientDetail.objects.create(patient=patient,symptom="Hormone levels",details=request.POST.get("hormone"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CT scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("ultrasound"):
                PatientDetail.objects.create(patient=patient,symptom="Ultrasound",file=request.FILES.get("ultrasound"))
            if request.FILES.get("cultures"):
                PatientDetail.objects.create(patient=patient,symptom="Cultures",file=request.FILES.get("cultures"))
            if request.FILES.get("biopsy"):
                PatientDetail.objects.create(patient=patient,symptom="Biopsy",file=request.FILES.get("biopsy"))

        if "Respiratory" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Respiratory rate",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Respiratory pattern",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Use of accessory muscles",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Cyanosis (Bluish discoloration)",details=request.POST.get("inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Chest expansion",details=request.POST.get("inspection_5"))
            PatientDetail.objects.create(patient=patient,symptom="Tenderness",details=request.POST.get("inspection_6"))
            PatientDetail.objects.create(patient=patient,symptom="Dullness or Hyperresonance",details=request.POST.get("inspection_7"))
            PatientDetail.objects.create(patient=patient,symptom="Breath sounds",details=request.POST.get("inspection_8"))
            PatientDetail.objects.create(patient=patient,symptom="Adventitious sound",details=request.POST.get("inspection_9"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            PatientDetail.objects.create(patient=patient,symptom="Arterial Blood Gases",details=request.POST.get("abg"))
            PatientDetail.objects.create(patient=patient,symptom="Sputum Culture",details=request.POST.get("sputum_culture"))
            PatientDetail.objects.create(patient=patient,symptom="Sputum Sensitivity",details=request.POST.get("sputum_sensitivity"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="HRCT scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("spirometry"):
                PatientDetail.objects.create(patient=patient,symptom="Spirometry",file=request.FILES.get("spirometry"))
            if request.FILES.get("xray"):
                PatientDetail.objects.create(patient=patient,symptom="X-Ray",file=request.FILES.get("xray"))
            if request.FILES.get("bronchoscopy"):
                PatientDetail.objects.create(patient=patient,symptom="Bronchoscopy",file=request.FILES.get("bronchoscopy"))
            PatientDetail.objects.create(patient=patient,symptom="Exercise Training",details=request.POST.get("exercise_training"))

        if "BDS" in doctor.sub_category.name:
            PatientDetail.objects.create(patient=patient,symptom="Face Symmetry",details=request.POST.get("inspection_1"))
            PatientDetail.objects.create(patient=patient,symptom="Swelling",details=request.POST.get("inspection_2"))
            PatientDetail.objects.create(patient=patient,symptom="Temporomandibular Joint",details=request.POST.get("inspection_3"))
            PatientDetail.objects.create(patient=patient,symptom="Lymph nodes",details=request.POST.get("inspection_4"))
            PatientDetail.objects.create(patient=patient,symptom="Lips",details=request.POST.get("inspection_5"))
            PatientDetail.objects.create(patient=patient,symptom="Buccal Mucosa",details=request.POST.get("inspection_6"))
            PatientDetail.objects.create(patient=patient,symptom="Tongue",details=request.POST.get("inspection_7"))
            PatientDetail.objects.create(patient=patient,symptom="Floor of mouth",details=request.POST.get("inspection_8"))
            PatientDetail.objects.create(patient=patient,symptom="Palate",details=request.POST.get("inspection_9"))
            PatientDetail.objects.create(patient=patient,symptom="Gingiva",details=request.POST.get("inspection_10"))
            PatientDetail.objects.create(patient=patient,symptom="Teeth",details=request.POST.get("inspection_11"))
            PatientDetail.objects.create(patient=patient,symptom="Mobility",details=request.POST.get("inspection_12"))
            PatientDetail.objects.create(patient=patient,symptom="Occlusion",details=request.POST.get("inspection_13"))
            PatientDetail.objects.create(patient=patient,symptom="Pocket depth",details=request.POST.get("inspection_14"))
            PatientDetail.objects.create(patient=patient,symptom="Gingival condition",details=request.POST.get("inspection_15"))
            PatientDetail.objects.create(patient=patient,symptom="CBC",details=request.POST.get("cbc"))
            if request.FILES.get("ct_scan"):
                PatientDetail.objects.create(patient=patient,symptom="CBCT scan",file=request.FILES.get("ct_scan"))
            if request.FILES.get("iopa"):
                PatientDetail.objects.create(patient=patient,symptom="IOPA",file=request.FILES.get("iopa"))
            if request.FILES.get("xray"):
                PatientDetail.objects.create(patient=patient,symptom="X-Ray",file=request.FILES.get("xray"))
            if request.FILES.get("opg"):
                PatientDetail.objects.create(patient=patient,symptom="OPG",file=request.FILES.get("opg"))

        return redirect('prescription')
        

    context={
        'doctor': doctor,
        'sub_valid': Subscription.objects.get(doctor=doctor).is_active,
    }
    return render(request,"dapp/dashboard-prescription-create.html",context)

def dashboard_rawprescription(request,pk):
    doctor = Doctor.objects.get(bmdc=get_username(request))
    patient = Patient.objects.filter(pid=pk)[0]
    context = {
        'patient': patient,
        'sub_valid': Subscription.objects.get(doctor=doctor).is_active,
    }
    return render(request,"dapp/dashboard-prescription-raw.html",context)

















@login_required(login_url="/log-in/")
def dashboard_tools(request):
    if is_student(request):
        context={
            'is_student':True,
            'sub_valid': StudentSubscription.objects.get(student=Student.objects.get(sid=get_username(request))).is_active
        }
    else:
        context={
            'is_student':False,
            'sub_valid': Subscription.objects.get(doctor=Doctor.objects.get(bmdc=get_username(request))).is_active,
        }
    return render(request,"dapp/dashboard-tools.html",context)

@require_POST
def dashboard_rqst_tools(request):
    toolname = request.POST.get("toolname")
    username = get_username(request)
    toolrequest = ToolRequest.objects.create(toolname=toolname,username=username)
    return redirect("tools")

@login_required(login_url="/log-in/")
def bmi(request):
    if is_student(request):
        context={
            'is_student':True,
            'sub_valid': StudentSubscription.objects.get(student=Student.objects.get(sid=get_username(request))).is_active
        }
    else:
        context={
            'is_student':False,
            'sub_valid': Subscription.objects.get(doctor=Doctor.objects.get(bmdc=get_username(request))).is_active,
        }
    return render(request,"dapp/tools/bmi.html",context)

@login_required(login_url="/log-in/")
def crcl(request):
    if is_student(request):
        context={
            'is_student':True,
            'sub_valid': StudentSubscription.objects.get(student=Student.objects.get(sid=get_username(request))).is_active
        }
    else:
        context={
            'is_student':False,
            'sub_valid': Subscription.objects.get(doctor=Doctor.objects.get(bmdc=get_username(request))).is_active,
        }
    return render(request,"dapp/tools/CrCl.html",context)

@login_required(login_url="/log-in/")
def cha2ds2_vasc(request):
    if is_student(request):
        context={
            'is_student':True,
            'sub_valid': StudentSubscription.objects.get(student=Student.objects.get(sid=get_username(request))).is_active
        }
    else:
        context={
            'is_student':False,
            'sub_valid': Subscription.objects.get(doctor=Doctor.objects.get(bmdc=get_username(request))).is_active,
        }
    return render(request,"dapp/tools/CHA2DS2-VASc.html",context)

@login_required(login_url="/log-in/")
def apgar(request):
    if is_student(request):
        context={
            'is_student':True,
            'sub_valid': StudentSubscription.objects.get(student=Student.objects.get(sid=get_username(request))).is_active
        }
    else:
        context={
            'is_student':False,
            'sub_valid': Subscription.objects.get(doctor=Doctor.objects.get(bmdc=get_username(request))).is_active,
        }
    return render(request,"dapp/tools/apgar.html",context)

@login_required(login_url="/log-in/")
def gfr(request):
    if is_student(request):
        context={
            'is_student':True,
            'sub_valid': StudentSubscription.objects.get(student=Student.objects.get(sid=get_username(request))).is_active
        }
    else:
        context={
            'is_student':False,
            'sub_valid': Subscription.objects.get(doctor=Doctor.objects.get(bmdc=get_username(request))).is_active,
        }
    return render(request,"dapp/tools/gfr.html",context)

@login_required(login_url="/log-in/")
def meld(request):
    if is_student(request):
        context={
            'is_student':True,
            'sub_valid': StudentSubscription.objects.get(student=Student.objects.get(sid=get_username(request))).is_active
        }
    else:
        context={
            'is_student':False,
            'sub_valid': Subscription.objects.get(doctor=Doctor.objects.get(bmdc=get_username(request))).is_active,
        }
    return render(request,"dapp/tools/meld.html",context)

@login_required(login_url="/log-in/")
def pedgrowthchart(request):
    if is_student(request):
        context={
            'is_student':True,
            'sub_valid': StudentSubscription.objects.get(student=Student.objects.get(sid=get_username(request))).is_active
        }
    else:
        context={
            'is_student':False,
            'sub_valid': Subscription.objects.get(doctor=Doctor.objects.get(bmdc=get_username(request))).is_active,
        }
    return render(request,"dapp/tools/pedgrowthchart.html",context)

@login_required(login_url="/log-in/")
def framinghamrisk(request):
    if is_student(request):
        context={
            'is_student':True,
            'sub_valid': StudentSubscription.objects.get(student=Student.objects.get(sid=get_username(request))).is_active
        }
    else:
        context={
            'is_student':False,
            'sub_valid': Subscription.objects.get(doctor=Doctor.objects.get(bmdc=get_username(request))).is_active,
        }
    return render(request,"dapp/tools/framinghamrisk.html",context)




















@login_required(login_url="/log-in/")
def dashboard_drugs(request):
    if request.method == "GET":
        if request.GET.get('query') == "all":
            drugs = Drug.objects.all()
            context = {
                'drugs': drugs,
                'is_student': is_student(request),
                'sub_valid': sub_validity_check(request),
            }
            return render(request,"dapp/dashboard-drugs.html",context)
    if request.method == "POST":
        text = request.POST.get("text")
        pk = request.POST.get("query")
        if pk == "brand":
            drugs = Drug.objects.filter(brand__icontains=text)
            context = {
                'drugs':drugs,
                'is_student': is_student(request),
                'sub_valid': sub_validity_check(request),
            }
            return render(request,"dapp/dashboard-drugs.html",context)
        if pk == "generic":
            drugs = Drug.objects.filter(generic__icontains=text)
            context = {
                'drugs':drugs,
                'is_student': is_student(request),
                'sub_valid': sub_validity_check(request),
            }
            return render(request,"dapp/dashboard-drugs.html",context)
        if pk == "id":
            drugs = Drug.objects.filter(drug_id__icontains=text)
            context = {
                'drugs':drugs,
                'is_student': is_student(request),
                'sub_valid': sub_validity_check(request),
            }
            return render(request,"dapp/dashboard-drugs.html",context)
    drugs = Drug.objects.all()
    context={
        'drugs':drugs[:20],
        'is_student': is_student(request),
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/dashboard-drugs.html",context)

@login_required(login_url="/log-in/")
def dashboard_drug(request,pk):
    drugs = Drug.objects.filter(drug_id=pk)
    context = {
        'drug':drugs[0],
        'is_student': is_student(request),
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/dashboard-drug.html",context)

@login_required(login_url="/log-in/")
def drugsapi(request):
    if request.method == "get" or request.method == "GET":
        query = request.GET.get('query')
        drugs = list(Drug.objects.filter(brand__icontains=query).values())
        return JsonResponse(drugs,safe=False)
        

















@login_required(login_url="/log-in/")
def dashboard_forum(request):
    doctor_posts = Post.objects.all()
    student_posts = StudentPost.objects.all()
    posts = list(chain(doctor_posts,student_posts))
    if is_student(request):
        student = Student.objects.get(sid=get_username(request))
        context={
            'posts': posts,
            'student': student,
            'is_student': is_student(request),
            'sub_valid': sub_validity_check(request),
        }
    else:
        doctor = Doctor.objects.get(bmdc=get_username(request))
        context={
            'posts': posts,
            'doctor': doctor,
            'is_student': is_student(request),
            'sub_valid': sub_validity_check(request),
        }
    return render(request,"dapp/dashboard-forum.html",context)

@login_required(login_url="/log-in/")
def createpost(request):
    if request.method == "POST":
        text = request.POST.get('text')
        images = request.FILES.getlist('images')

        if is_student(request):
            post = StudentPost.objects.create(body=text,id=generate_id("p",10),student=Student.objects.get(sid=get_username(request)))
        else:
            post = Post.objects.create(body=text,id=generate_id("p",10),doctor=Doctor.objects.get(bmdc=get_username(request)))

        for image in images[:3]:
            if is_student(request):
                StudentPostImage.objects.create(post=post,image=image)
            else:
                PostImage.objects.create(post=post,image=image)
        
        return redirect('post',pk=post.id)
    
    context = {
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/dashboard-createpost.html",context)

@login_required(login_url="/log-in/")
def post(request,pk):
    try:
        instance = Post.objects.get(id=pk)
        total_likes = []
        total_comments = []
        likes = PostLike.objects.filter(post=instance)
        slikes = StudentPostLike.objects.filter(post=instance)
        total_likes = list(chain(likes,slikes))
        comments = Comment.objects.filter(post=instance)
        scomments = StudentComment.objects.filter(post=instance)
        total_comments = list(chain(comments,scomments))
        if is_student(request):
            student = Student.objects.get(sid=get_username(request))
            saved = False if len(StudentSaved.objects.filter(post=instance,student=student)) == 0 else True
        else:
            doctor = Doctor.objects.get(bmdc=get_username(request))
            saved = False if len(Saved.objects.filter(post=instance,doctor=doctor)) == 0 else True
    except:
        instance = StudentPost.objects.get(id=pk)
        total_likes = []
        total_comments = []
        likes = PostLike2.objects.filter(post=instance)
        slikes = StudentPostLike2.objects.filter(post=instance)
        total_likes = list(chain(likes,slikes))
        comments = Comment2.objects.filter(post=instance)
        scomments = StudentComment2.objects.filter(post=instance)
        total_comments = list(chain(comments,scomments))
        if is_student(request):
            student = Student.objects.get(sid=get_username(request))
            saved = False if len(StudentSaved2.objects.filter(post=instance,student=student)) == 0 else True
        else:
            doctor = Doctor.objects.get(bmdc=get_username(request))
            saved = False if len(Saved2.objects.filter(post=instance,doctor=doctor)) == 0 else True

    context = {
        'post': instance,
        'postlikes': total_likes,
        'comments': total_comments,
        'saved': saved,
        'is_student': is_student(request),
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/dashboard-post.html",context)

@login_required(login_url="/log-in/")
def savepost(request,pk):
    try:
        instance = Post.objects.get(id=pk)
        try:
            doctor = Doctor.objects.get(bmdc=get_username(request))
            if len(Saved.objects.filter(post=instance,doctor=doctor)) == 0:
                Saved.objects.create(post=instance,doctor=doctor)
            else:
                Saved.objects.filter(post=instance,doctor=doctor).delete
        except:
            student = Student.objects.get(sid=get_username(request))
            if len(StudentSaved.objects.filter(post=instance,student=student)) == 0:
                StudentSaved.objects.create(post=instance,student=student)
            else:
                StudentSaved.objects.filter(post=instance,student=student).delete
    except:
        instance = StudentPost.objects.get(id=pk)
        try:
            doctor = Doctor.objects.get(bmdc=get_username(request))
            if len(Saved2.objects.filter(post=instance,doctor=doctor)) == 0:
                Saved2.objects.create(post=instance,doctor=doctor)
            else:
                Saved2.objects.filter(post=instance,doctor=doctor).delete
        except:
            student = Student.objects.get(sid=get_username(request))
            if len(StudentSaved2.objects.filter(post=instance,student=student)) == 0:
                StudentSaved2.objects.create(post=instance,student=student)
            else:
                StudentSaved2.objects.filter(post=instance,student=student).delete
    return redirect('post',pk=instance.id)

@login_required(login_url="/log-in/")
def postlike(request,pk):
    try:
        post = Post.objects.get(id=pk)
        try:
            doctor = Doctor.objects.get(bmdc=get_username(request))
            if len(PostLike.objects.filter(post=post,doctor=doctor)) == 0:
                PostLike.objects.create(post=post,doctor=doctor)
                post.total_likes +=1
                post.save()
                n = Notification.objects.create(doctor=Doctor.objects.get(bmdc=post.owner_id),text=f"{doctor.name} liked your post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                h = History.objects.create(doctor=doctor,text=f"You liked {post.owner_name}'s post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                n.save()
                h.save()
                return JsonResponse({'likes':post.total_likes})
            else:
                return JsonResponse({'likes':post.total_likes})
        except:
            student = Student.objects.get(sid=get_username(request))
            if len(StudentPostLike.objects.filter(post=post,student=student)) == 0:
                StudentPostLike.objects.create(post=post,student=student)
                post.total_likes +=1
                post.save()
                n = Notification.objects.create(doctor=Doctor.objects.get(bmdc=post.owner_id),text=f"{student.name} liked your post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                h = StudentHistory.objects.create(student=student,text=f"You liked {post.owner_name}'s post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                n.save()
                h.save()
                return JsonResponse({'likes':post.total_likes})
            else:
                return JsonResponse({'likes':post.total_likes})
    except:
        post = StudentPost.objects.get(id=pk)
        try:
            doctor = Doctor.objects.get(bmdc=get_username(request))
            if len(PostLike2.objects.filter(post=post,doctor=doctor)) == 0:
                PostLike2.objects.create(post=post,doctor=doctor)
                post.total_likes +=1
                post.save()
                n = StudentNotification.objects.create(student=Student.objects.get(sid=post.owner_id),text=f"{doctor.name} liked your post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                h = History.objects.create(doctor=doctor,text=f"You liked {post.owner_name}'s post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                n.save()
                h.save()
                return JsonResponse({'likes':post.total_likes})
            else:
                return JsonResponse({'likes':post.total_likes})
        except:
            student = Student.objects.get(sid=get_username(request))
            if len(StudentPostLike2.objects.filter(post=post,student=student)) == 0:
                StudentPostLike2.objects.create(post=post,student=student)
                post.total_likes +=1
                post.save()
                n = StudentNotification.objects.create(student=Student.objects.get(bmdc=post.owner_id),text=f"{student.name} liked your post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                h = StudentHistory.objects.create(student=student,text=f"You liked {post.owner_name}'s post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                n.save()
                h.save()
                return JsonResponse({'likes':post.total_likes})
            else:
                return JsonResponse({'likes':post.total_likes})

@login_required(login_url="/log-in/")
def postlikes(request,pk):
    try:
        post = Post.objects.get(id=pk)
        users = PostLike.objects.filter(post=post)
        susers = StudentPostLike.objects.filter(post=post)
        user_list = [{"name": user.doctor.name, "bmdc": user.doctor.bmdc} for user in users] + [{"name": user.student.sid, "bmdc": user.student.sid} for user in susers]
    except:
        post = StudentPost.objects.get(id=pk)
        users = PostLike2.objects.filter(post=post)
        susers = StudentPostLike2.objects.filter(post=post)
        user_list = [{"name": user.doctor.name, "bmdc": user.doctor.bmdc} for user in users] + [{"name": user.student.sid, "bmdc": user.student.sid} for user in susers]
    return JsonResponse({"users": user_list})

@csrf_exempt
def postcomment(request,pk):
    if request.method == "POST":
        comment_text = request.POST.get("comment_text")
        comment_image = request.FILES.get("comment_image")

        try:
            post = Post.objects.get(id=pk)
            try:
                doctor = Doctor.objects.get(bmdc=get_username(request))
                comment = Comment.objects.create(
                    id=generate_id("c",10),
                    post=post,
                    doctor=doctor,
                    text=comment_text,
                    image=comment_image
                )
                post.total_comments += 1
                n = Notification.objects.create(doctor=Doctor.objects.get(bmdc=post.owner_id),text=f"{doctor.name} commented on your post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                h = History.objects.create(doctor=doctor,text=f"You commented on {post.owner_name}'s post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                n.save()
                h.save()
            except:
                student=Student.objects.get(sid=get_username(request))
                comment = StudentComment.objects.create(
                id=generate_id("c",10),
                post=post,
                student=student,
                text=comment_text,
                image=comment_image
                )
                post.total_comments += 1
                n = Notification.objects.create(doctor=Doctor.objects.get(bmdc=post.owner_id),text=f"{student.name} commented on your post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                h = StudentHistory.objects.create(student=student,text=f"You commented on {post.owner_name}'s post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                n.save()
                h.save()
        except:
            post = StudentPost.objects.get(id=pk)
            try:
                doctor = Doctor.objects.get(bmdc=get_username(request))
                comment = Comment2.objects.create(
                    id=generate_id("c",10),
                    post=post,
                    doctor=Doctor.objects.get(bmdc=get_username(request)),
                    text=comment_text,
                    image=comment_image
                )
                post.total_comments += 1
                n = StudentNotification.objects.create(student=Student.objects.get(sid=post.owner_id),text=f"{doctor.name} commented on your post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                h = History.objects.create(doctor=doctor,text=f"You commented on {post.owner_name}'s post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                n.save()
                h.save()
            except:
                student=Student.objects.get(sid=get_username(request))
                comment = StudentComment2.objects.create(
                id=generate_id("c",10),
                post=post,
                student=Student.objects.get(sid=get_username(request)),
                text=comment_text,
                image=comment_image
                )
                post.total_comments += 1
                n = StudentNotification.objects.create(student=Student.objects.get(sid=post.owner_id),text=f"{student.name} commented on your post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                h = StudentHistory.objects.create(student=student,text=f"You commented on {post.owner_name}'s post.",link="https://prescribemate.com/forum/post/"+post.id+"/")
                n.save()
                h.save()
        return redirect('post',pk=post.id)




















@login_required(login_url="/log-in/")
def dashboard_settings(request):
    context={
        'is_student':is_student(request),
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/dashboard-settings.html",context)

@login_required(login_url="/log-in/")
def profile(request,pk):
    try:
        student = Student.objects.get(sid=pk)
        context={
            'student': student,
            's': True,
            'is_student':is_student(request),
            'sub_valid': sub_validity_check(request),
        }
    except:
        doctor = Doctor.objects.get(bmdc=pk)
        context={
            'doctor': doctor,
            's': False,
            'is_student':is_student(request),
            'sub_valid': sub_validity_check(request),
        }
    return render(request,"dapp/settings/profile.html",context)

@login_required(login_url="/log-in/")
def dashboard_profileself(request):
    if is_student(request):
        student = Student.objects.get(sid=get_username(request))
        context={
            'student': student,
            'is_student':is_student(request),
            'sub_valid': sub_validity_check(request),
        }
    else:
        doctor = Doctor.objects.get(bmdc=get_username(request))
        cats = DoctorCategory.objects.all()
        context={
            'doctor': doctor,
            'cats': cats,
            'is_student':is_student(request),
            'sub_valid': sub_validity_check(request),
        }
    return render(request,"dapp/settings/dashboard_profileself.html",context)

@login_required(login_url="/log-in/")
def updateidentity(request):
    if request.method == "POST":
        doctor = Doctor.objects.get(bmdc=get_username(request))
        sc = request.POST.get("subcategory")
        doctor.sub_category = DoctorSubCategory.objects.get(name=sc)
        doctor.category = doctor.sub_category.category
        doctor.bsub_category = sub_category_conversion(sc)
        doctor.save()
        return redirect('profile-self')

@login_required(login_url="/log-in/")
def updatecontact(request):
    if request.method == "POST":
        try:
            doctor = Doctor.objects.get(bmdc=get_username(request))
            doctor.phone = request.POST.get("phone")
            doctor.email = request.POST.get("email")
            doctor.save()
            return redirect('profile-self')
        except:
            student = Student.objects.get(sid=get_username(request))
            student.phone = request.POST.get("phone")
            student.email = request.POST.get("email")
            student.save()
            return redirect('profile-self')

@login_required(login_url="/log-in/")    
def updatejobs(request):
    if request.method == "POST":
        doctor = Doctor.objects.get(bmdc=get_username(request))
        doctor.job = request.POST.get("job")
        doctor.chamber = request.POST.get("chamber")
        doctor.save()
        return redirect('profile-self')

@login_required(login_url="/log-in/")
def updatequalification(request):
    if request.method == "POST":
        doctor = Doctor.objects.get(bmdc=get_username(request))
        doctor.qualification += request.POST.get("qualification")
        doctor.save()
        return redirect('profile-self')

@login_required(login_url="/log-in/")
def updatebangla(request):
    if request.method == "POST":
        doctor = Doctor.objects.get(bmdc=get_username(request))
        doctor.bname = request.POST.get("bname")
        doctor.bqualification = request.POST.get("bqualification")
        doctor.save()
        return redirect('profile-self')
    
@login_required(login_url="/log-in/")
def changepassword(request):
    if request.method == "POST":
        try:
            doctor = Doctor.objects.get(bmdc=get_username(request))
            if request.POST.get("password") == request.POST.get("confirmpassword"):
                doctor.password += request.POST.get("password")
                doctor.save()
                Notification.objects.create(doctor=doctor,text="Password changed successfully",link="#")
            else:
                Notification.objects.create(doctor=doctor,text="Password change failed",link="#")
            return redirect('profile-self')
        except:
            student = Student.objects.get(sid=get_username(request))
            if request.POST.get("password") == request.POST.get("confirmpassword"):
                student.password += request.POST.get("password")
                student.save()
                StudentNotification.objects.create(student=student,text="Password changed successfully",link="#")
            else:
                StudentNotification.objects.create(student=student,text="Password change failed",link="#")
            return redirect('profile-self')

@login_required(login_url="/log-in/")
def updateimage(request):
    if request.method == "POST":
        try:
            doctor = Doctor.objects.get(bmdc=get_username(request))
            doctor.image = request.FILES["image"]
            doctor.save()
            return redirect('profile-self')
        except:
            student = Student.objects.get(sid=get_username(request))
            student.image = request.FILES["image"]
            student.save()
            return redirect('profile-self')

@login_required(login_url="/log-in/")
def dashboard_notification(request):
    try:
        doctor = Doctor.objects.get(bmdc=get_username(request))
        notifications = Notification.objects.filter(doctor=doctor)
    except:
        student = Student.objects.get(sid=get_username(request))
        notifications = StudentNotification.objects.filter(student=student)
    if len(notifications) > 10:
        notis = notifications[:10]
    else:
        notis = notifications
    context={
        'notis': notis,
        'notis_len': len(notis),
        'is_student':is_student(request),
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/settings/dashboard_notification.html",context)

@login_required(login_url="/log-in/")
def dashboard_clearnotification(request):
    try:
        doctor = Doctor.objects.get(bmdc=get_username(request))
        Notification.objects.filter(doctor=doctor).delete()
        notifications = Notification.objects.filter(doctor=doctor)
    except:
        student = Student.objects.get(sid=get_username(request))
        StudentNotification.objects.filter(student=student).delete()
        notifications = StudentNotification.objects.filter(student=student)
    if len(notifications) > 10:
        notis = notifications[:10]
    else:
        notis = notifications
    context={
        'notis': notis,
        'is_student':is_student(request),
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/settings/dashboard_notification.html",context)

@login_required(login_url="/log-in/")
def dashboard_enableai(request):
    context={
        'is_student':is_student(request),
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/settings/dashboard_enableai.html",context)

@login_required(login_url="/log-in/")
def dashboard_customtheme(request):
    doctor = Doctor.objects.get(bmdc=get_username(request))
    general_themes = Theme.objects.filter(custom=False)
    custom_themes = Theme.objects.filter(name="custom"+doctor.bmdc)
    themes = []
    themes += custom_themes
    themes += general_themes
    context={
        'doctor': doctor,
        'themes': themes,
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/settings/dashboard_customtheme.html",context)

@login_required(login_url="/log-in/")
def dashboard_selecttheme(request,pk):
    doctor = Doctor.objects.get(bmdc=get_username(request))
    theme = Theme.objects.get(name=pk)
    try:
        instance = SelectedTheme.objects.filter(doctor=doctor)
        instance[0].theme = theme
        return redirect('customtheme')
    except:
        instance = SelectedTheme.objects.create(doctor=doctor,theme=theme)
        return redirect('customtheme')

@login_required(login_url="/log-in/")
def dashboard_customthemerequest(request):
    doctor = Doctor.objects.get(bmdc=get_username(request))
    ThemeRequest.objects.create(doctor=doctor,text=request.POST.get("themename"))
    return redirect('customtheme')

@login_required(login_url="/log-in/")
def dashboard_customtoolbar(request):
    context={
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/settings/dashboard_customtoolbar.html",context)

@login_required(login_url="/log-in/")
def dashboard_customfeed(request):
    context={
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/settings/dashboard_customfeed.html",context)

@login_required(login_url="/log-in/")
def dashboard_changesubscription(request):
    try:
        doctor = Doctor.objects.get(bmdc=get_username(request))
        subscription = Subscription.objects.get(doctor=doctor)
    except:
        student = Student.objects.get(sid=get_username(request))
        subscription = StudentSubscription.objects.get(student=student)
    context={
        'subscription':subscription,
        'is_student':is_student(request),
        'sub_valid': True,
    }
    return render(request,"dapp/settings/dashboard_changesubscription.html",context)

@login_required(login_url="/log-in/")
def dashboard_changecategory(request):
    context={
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/settings/dashboard_changecategory.html",context)

@login_required(login_url="/log-in/")
def dashboard_history(request):
    try:
        doctor = Doctor.objects.get(bmdc=get_username(request))
        hs = History.objects.filter(doctor=doctor)
    except:
        student = Student.objects.get(sid=get_username(request))
        hs = StudentHistory.objects.filter(student=student)
    context={
        'hs': hs,
        'is_student':is_student(request),
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/settings/dashboard_history.html",context)

@login_required(login_url="/log-in/")
def dashboard_saved(request):
    try:
        doctor = Doctor.objects.get(bmdc=get_username(request))
        ss = Saved.objects.filter(doctor=doctor)
        ss2 = Saved2.objects.filter(doctor=doctor)
        t_ss = list(chain(ss,ss2))
    except:
        student = Student.objects.get(sid=get_username(request))
        ss = StudentSaved.objects.filter(student=student)
        ss2 = StudentSaved2.objects.filter(student=student)
        t_ss = list(chain(ss,ss2))
    context={
        'ss': t_ss,
        'is_student':is_student(request),
        'sub_valid': sub_validity_check(request),
    }
    return render(request,"dapp/settings/dashboard_saved.html",context)














def api_doctor(request,pk):
    try:
        try:
            doctor = Doctor.objects.get(bmdc=pk)
            doctor_info = {
                'username': doctor.bmdc,
                'name': doctor.name,
                'email': doctor.email,
                'phone': doctor.phone,
            }
            return JsonResponse(doctor_info)
        except:
            student = Student.objects.get(sid=pk)
            doctor_info = {
                'username': student.sid,
                'name': student.name,
                'email': student.email,
                'phone': student.phone,
            }
            return JsonResponse(doctor_info)
    except:
        doctor_info = {
            'username': 'N/A',
            'name': 'N/A',
            'email': 'N/A',
            'phone': 'N/A',
        }
        return JsonResponse(doctor_info)

def check_tran_id(s):
    response = requests.get("https://siuchtechnologies.com/api/check_tran_id/"+str(s)+"/")
    return response.json()["status"]

def add_subscription(request,pk,pk2,pk3):
    try:
        doctor = Doctor.objects.get(bmdc=pk)
        if check_tran_id(pk3) == "True":
            subscription = Subscription.objects.get(doctor=doctor)
            if pk2 == "200":
                subscription.subscription_type = "monthly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=30)
                subscription.save()
            elif pk2 == "550":
                subscription.subscription_type = "quarterly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=90)
                subscription.save()
            elif pk2 == "1100":
                subscription.subscription_type = "half-yearly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=180)
                subscription.save()
            elif pk2 == "2000":
                subscription.subscription_type = "yearly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=365)
                subscription.save()
            elif pk2 == "10000":
                subscription.subscription_type = "five-yearly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=1825)
                subscription.save()
            n = Notification.objects.create(doctor=doctor,text="Your subscription has been extended. Check now!",link="https://prescribemate.com/dashboard/settings/notification/")
            n.save()
            return JsonResponse({'status':'Success'})
        else:
            return JsonResponse({'status':'Failed'})
    except:
        student = Student.objects.get(sid=pk)
        if check_tran_id(pk3) == "True":
            subscription = StudentSubscription.objects.get(student=student)
            if pk2 == "50":
                subscription.subscription_type = "monthly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=30)
                subscription.save()
            elif pk2 == "150":
                subscription.subscription_type = "quarterly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=90)
                subscription.save()
            elif pk2 == "300":
                subscription.subscription_type = "half-yearly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=180)
                subscription.save()
            elif pk2 == "500":
                subscription.subscription_type = "yearly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=365)
                subscription.save()
            elif pk2 == "2500":
                subscription.subscription_type = "five-yearly"
                subscription.is_active = True
                subscription.expiry_date += timezone.timedelta(days=1825)
                subscription.save()
            n = StudentNotification.objects.create(student=student,text="Your subscription has been extended. Check now!",link="https://prescribemate.com/dashboard/settings/notification/")
            n.save()
            return JsonResponse({'status':'Success'})
        else:
            return JsonResponse({'status':'Failed'})


















def checkout(request):
    if request.method=="POST":
        stype = request.POST.get("stype")
        if is_student(request):
            student = Student.objects.get(sid = get_username(request))
            subscription = StudentSubscription.objects.get(student=student)
            subscription_type = stype
            if stype == "monthly":
                expiry_date = subscription.expiry_date + timezone.timedelta(days=30)
                amount = "50"

            elif stype == "quarterly":
                expiry_date = subscription.expiry_date + timezone.timedelta(days=90)
                amount = "150"
                
            elif stype == "halfyearly":
                expiry_date = subscription.expiry_date + timezone.timedelta(days=180)
                amount = "300"
                
            elif stype == "yearly":
                expiry_date = subscription.expiry_date + timezone.timedelta(days=365)
                amount = "500"
                
            else:
                expiry_date = subscription.expiry_date + timezone.timedelta(days=1825)
                amount = "2500"

            subscription.save()
            context = {
                'stype': stype,
                'customer': student,
                'customer_id': student.sid,
                'subscription_type': subscription_type,
                'amount': amount,
                'expiry_date': expiry_date,
                'start_date': timezone.now(),
                'sub_valid': True,
            }
        else:
            doctor = Doctor.objects.get(bmdc = get_username(request))
            subscription = Subscription.objects.get(doctor=doctor)
            subscription_type = stype
            if stype == "monthly":
                expiry_date = subscription.expiry_date + timezone.timedelta(days=30)
                amount = "200"
            
            elif stype == "quarterly":
                expiry_date = subscription.expiry_date + timezone.timedelta(days=90)
                amount = "550"
                
            elif stype == "halfyearly":
                expiry_date = subscription.expiry_date + timezone.timedelta(days=180)
                amount = "1100"
                
            elif stype == "yearly":
                expiry_date = subscription.expiry_date + timezone.timedelta(days=365)
                amount = "2000"
                
            else:
                expiry_date = subscription.expiry_date + timezone.timedelta(days=1825)
                amount = "10000"

            subscription.save()
            context = {
                'stype': stype,
                'customer': doctor,
                'customer_id': doctor.bmdc,
                'subscription_type': subscription_type,
                'amount': amount,
                'expiry_date': expiry_date,
                'start_date': timezone.now(),
                'sub_valid': True,
            }
        return render(request,"dapp/checkout.html",context)
    if is_student(request):
        student = Student.objects.get(get_username(request))
        context={
            'customer': student,
            'sub_valid': True,
        }
    else:
        doctor = Doctor.objects.get(get_username(request))
        context={
            'customer': doctor,
            'sub_valid': True,
        }
    return render(request,"dapp/checkout.html",context)