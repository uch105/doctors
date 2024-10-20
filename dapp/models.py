from django.db import models
from django.db.models import Model
from django.utils import timezone
from datetime import timedelta

class ReportLogin(models.Model):
    bmdc = models.CharField(max_length=255,null=True,blank=True)
    d = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.bmdc

class DoctorCategory(models.Model):
    name = models.CharField(max_length=255,primary_key=True)

    def __str__(self):
        return self.name
    
class DoctorSubCategory(models.Model):
    category = models.ForeignKey(DoctorCategory,on_delete=models.CASCADE,related_name="subcategories",default="MBBS")
    name = models.CharField(max_length=255,primary_key=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    bmdc = models.CharField(max_length=255,primary_key=True)
    password = models.CharField(max_length=255,default="1234")
    name = models.CharField(max_length=255,null=True,blank=True)
    phone = models.CharField(max_length=255,unique=True,default="Null")
    email = models.CharField(max_length=255,unique=True,default="Null")
    image = models.ImageField(upload_to="images/doctors/")
    reg_year = models.CharField(max_length=255,default="Null")
    valid_till = models.CharField(max_length=255,default="Null")
    blood_group = models.CharField(max_length=255,default="Null")
    gender = models.CharField(max_length=255,default="Null")
    fname = models.CharField(max_length=255,default="Null")
    mname = models.CharField(max_length=255,default="Null")
    dob = models.CharField(max_length=255,default="Null")
    status = models.BooleanField(default=False)
    job = models.CharField(max_length=255,default="Null")
    chamber = models.CharField(max_length=255,default="Null")
    qualification = models.CharField(max_length=1000,default="Null")
    category = models.ForeignKey(DoctorCategory,on_delete=models.CASCADE,related_name="categories")
    sub_category = models.ForeignKey(DoctorSubCategory,on_delete=models.CASCADE,related_name="subcategories")
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Subscription(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,unique=True)
    subscription_type = models.CharField(max_length=255,default="trial")
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateField(default=timezone.now()+timezone.timedelta(days=7))

    def __str__(self):
        return f"{self.doctor.name} - {'Active' if self.is_active else 'Expired'}"
    
    @property
    def is_subscription_valid(self):
        return self.expiry_date > timezone.now()
    
    @property
    def days_left(self):
        if self.is_subscription_valid():
            return (self.expiry_date - timezone.now()).days
        else:
            self.is_active = False
        return 0

class MedicalCollege(models.Model):
    name = models.CharField(max_length=500,null=True,blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    sid = models.CharField(max_length=255,primary_key=True)
    password = models.CharField(max_length=255,default="1234")
    name = models.CharField(max_length=255,null=True,blank=True)
    phone = models.CharField(max_length=255,unique=True,default="Null")
    email = models.CharField(max_length=255,unique=True,default="Null")
    image = models.ImageField(upload_to="images/students/")
    blood_group = models.CharField(max_length=255,default="Null")
    gender = models.CharField(max_length=255,default="Null")
    dob = models.CharField(max_length=255,default="Null")
    institute = models.ForeignKey(MedicalCollege,related_name="clgstudents",on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " ( " + self.institute.name + " )"

class StudentSubscription(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE,unique=True)
    subscription_type = models.CharField(max_length=255,default="trial")
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateField(default=timezone.now()+timezone.timedelta(days=7))

    def __str__(self):
        return f"{self.student.name} - {'Active' if self.is_active else 'Expired'}"
    
    @property
    def is_subscription_valid(self):
        return self.expiry_date > timezone.now()
    
    @property
    def days_left(self):
        if self.is_subscription_valid():
            return (self.expiry_date - timezone.now()).days
        else:
            self.is_active = False
        return 0
    
class Post(models.Model):
    id = models.CharField(max_length=100,primary_key=True)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name="posts")
    date_time = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    total_likes = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)

    @property
    def owner_name(self):
        return self.doctor.name
    
    @property
    def owner_image(self):
        return self.doctor.image
    
    @property
    def owner_id(self):
        return self.doctor.bmdc

    def __str__(self):
        return self.doctor.name+" created "+str(self.date_time)

class StudentPost(models.Model):
    id = models.CharField(max_length=100,primary_key=True)
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name="sposts")
    date_time = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    total_likes = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)

    @property
    def owner_name(self):
        return self.student.name
    
    @property
    def owner_image(self):
        return self.student.image
    
    @property
    def owner_id(self):
        return self.student.sid

    def __str__(self):
        return self.student.name+" created "+str(self.date_time)

class StudentPostImage(models.Model):
    post = models.ForeignKey(StudentPost, related_name="images",on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/post_images/")

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name="images",on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/post_images/")

class PostLike(models.Model):
    post = models.ForeignKey(Post,related_name="likelist",on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)

    @property
    def owner_name(self):
        return self.doctor.name
    
    @property
    def owner_image(self):
        return self.doctor.image
    
    @property
    def owner_id(self):
        return self.doctor.bmdc

class StudentPostLike(models.Model):
    post = models.ForeignKey(Post,related_name="slikelist",on_delete=models.CASCADE)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)

    @property
    def owner_name(self):
        return self.student.name
    
    @property
    def owner_image(self):
        return self.student.image
    
    @property
    def owner_id(self):
        return self.student.sid

class PostLike2(models.Model):
    post = models.ForeignKey(StudentPost,related_name="likelist2",on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)

    @property
    def owner_name(self):
        return self.doctor.name
    
    @property
    def owner_image(self):
        return self.doctor.image
    
    @property
    def owner_id(self):
        return self.doctor.bmdc

class StudentPostLike2(models.Model):
    post = models.ForeignKey(StudentPost,related_name="slikelist2",on_delete=models.CASCADE)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)

    @property
    def owner_name(self):
        return self.student.name
    
    @property
    def owner_image(self):
        return self.student.image
    
    @property
    def owner_id(self):
        return self.student.sid

class Comment(models.Model):
    id = models.CharField(max_length=255,primary_key=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="comments")
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to="comment/",null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def owner_name(self):
        return self.doctor.name
    
    @property
    def owner_image(self):
        return self.doctor.image
    
    @property
    def owner_id(self):
        return self.doctor.bmdc

class StudentComment(models.Model):
    id = models.CharField(max_length=255,primary_key=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="scomments")
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to="comment/",null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def owner_name(self):
        return self.student.name
    
    @property
    def owner_image(self):
        return self.student.image
    
    @property
    def owner_id(self):
        return self.student.sid

class Comment2(models.Model):
    id = models.CharField(max_length=255,primary_key=True)
    post = models.ForeignKey(StudentPost,on_delete=models.CASCADE,related_name="comments2")
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to="comment/",null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def owner_name(self):
        return self.doctor.name
    
    @property
    def owner_image(self):
        return self.doctor.image
    
    @property
    def owner_id(self):
        return self.doctor.bmdc

class StudentComment2(models.Model):
    id = models.CharField(max_length=255,primary_key=True)
    post = models.ForeignKey(StudentPost,on_delete=models.CASCADE,related_name="scomments2")
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to="comment/",null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def owner_name(self):
        return self.student.name
    
    @property
    def owner_image(self):
        return self.student.image
    
    @property
    def owner_id(self):
        return self.student.sid


class Drug(models.Model):
    drug_id = models.CharField(max_length=100,null=True)
    brand = models.CharField(max_length=255,null=True,blank=True)
    generic = models.CharField(max_length=255,null=True,blank=True)
    manufacturer = models.CharField(max_length=255,null=True,blank=True)
    price = models.CharField(max_length=255,null=True,blank=True)
    class_name = models.CharField(max_length=255,null=True,blank=True)
    drugs_type = models.CharField(max_length=255,null=True,blank=True)
    drugs_for = models.CharField(max_length=255,null=True,blank=True)
    drugs_dose = models.CharField(max_length=255,null=True,blank=True)
    indication = models.TextField(null=True,blank=True)
    contraindication = models.TextField(null=True,blank=True)
    side_effect = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.brand

class ToolRequest(models.Model):
    username = models.CharField(max_length=255,null=True,blank=True)
    toolname = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return self.toolname
    
class Notification(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='notifications')
    text = models.CharField(max_length=1024,null=True,blank=True)
    link = models.CharField(max_length=255,null=True,blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.doctor.name} - {self.text[:30]}"
    
    @property
    def time_since(self):
        """Return how much time has passed since the notification was created."""
        delta = timezone.now() - self.timestamp
        if delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600}h"
        elif delta.seconds // 60 > 0:
            return f"{delta.seconds // 60}m"
        else:
            return "Just now"

class StudentNotification(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='snotifications')
    text = models.CharField(max_length=1024,null=True,blank=True)
    link = models.CharField(max_length=255,null=True,blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.name} - {self.text[:30]}"
    
    @property
    def time_since(self):
        """Return how much time has passed since the notification was created."""
        delta = timezone.now() - self.timestamp
        if delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600}h"
        elif delta.seconds // 60 > 0:
            return f"{delta.seconds // 60}m"
        else:
            return "Just now"
    
class History(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='histories')
    text = models.CharField(max_length=1024,null=True,blank=True)
    link = models.CharField(max_length=255,null=True,blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.doctor.name} - {self.text[:30]}"
    
    @property
    def time_since(self):
        """Return how much time has passed since the notification was created."""
        delta = timezone.now() - self.timestamp
        if delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600}h"
        elif delta.seconds // 60 > 0:
            return f"{delta.seconds // 60}m"
        else:
            return "Just now"

class StudentHistory(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='shistories')
    text = models.CharField(max_length=1024,null=True,blank=True)
    link = models.CharField(max_length=255,null=True,blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.name} - {self.text[:30]}"
    
    @property
    def time_since(self):
        """Return how much time has passed since the notification was created."""
        delta = timezone.now() - self.timestamp
        if delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600}h"
        elif delta.seconds // 60 > 0:
            return f"{delta.seconds // 60}m"
        else:
            return "Just now"


class Saved(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='saveds')
    post = models.ForeignKey(Post,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.doctor.name} - {self.post.id}"

class StudentSaved(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='ssaveds')
    post = models.ForeignKey(Post,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.name} - {self.post.id}"

class Saved2(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='saveds2')
    post = models.ForeignKey(StudentPost,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.doctor.name} - {self.post.id}"

class StudentSaved2(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='ssaveds2')
    post = models.ForeignKey(StudentPost,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.name} - {self.post.id}"

class Theme(models.Model):
    name = models.CharField(max_length=255,primary_key=True)
    image = models.ImageField(upload_to="images/themes/")
    custom = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ThemeRequest(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    text = models.CharField(max_length=1000,null=True,blank=True)

    def __str__(self):
        return self.doctor.name

class SelectedTheme(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name="selectedthemes")
    theme = models.ForeignKey(Theme,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.doctor.name} - {self.theme.name}"
    
class Patient(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name="patients")
    name = models.CharField(max_length=255,null=True,blank=True)
    age = models.CharField(max_length=2,null=True,blank=True)
    sex = models.CharField(max_length=255,null=True,blank=True)
    address = models.CharField(max_length=255,null=True,blank=True)
    contact = models.CharField(max_length=255,null=True,blank=True)
    occupation = models.CharField(max_length=255,null=True,blank=True)
    pdf = models.FileField(upload_to="files/",null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ( {self.sex} - {self.age} years )"

class Symptom(models.Model):
    dept = models.ForeignKey(DoctorSubCategory,on_delete=models.CASCADE,related_name="symptoms")
    parent = models.CharField(max_length=255,null=True,blank=True)
    