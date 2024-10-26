from django.http import JsonResponse,request
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
from .models import *
from decouple import config
from .bmdc import fetch_doctor_data








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
            instance = Doctor.objects.create(bmdc=c+bmdc,category=category,sub_category=sub_category,name=context['name'],reg_year=context['regyear'],valid_till=context['regvalidyear'],blood_group=context['bg'],status= True,dob=context['dob'],fname=context['fname'],mname=context['mname'])
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
    context={
        'doctor': doctor,
        'sub_valid': Subscription.objects.get(doctor=doctor).is_active,
    }
    return render(request,"dapp/dashboard-prescription.html",context)

@login_required(login_url="/log-in/")
def dashboard_createprescription(request):
    doctor = Doctor.objects.get(bmdc=get_username(request))
    context={
        'doctor': doctor,
        'sub_valid': Subscription.objects.get(doctor=doctor).is_active,
    }
    return render(request,"dapp/dashboard-prescription-create.html",context)

















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