from django.shortcuts import render,redirect
import urllib.request
import urllib.parse
import random 
import ssl
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from mainapp.models import *
# Create your views here.

def home(req):
    return render(req,'main-home.html')
def user_login(req):
    if req.method == 'POST':
        u_email = req.POST.get('email')
        u_password = req.POST.get('password')
        print( u_email,u_password)
        
        user_data = User.objects.get(Email = u_email)
        print(user_data)
        if user_data.Password == u_password:
            if user_data.Otp_Status == 'verified' and user_data.User_Status=='accepted':
                req.session['User_id'] = user_data.User_id
                messages.success(req, 'You are logged in..')
                user_data.No_Of_Times_Login += 1
                user_data.save()
                return redirect('user_dashboard')
            elif user_data.Otp_Status == 'verified' and user_data.User_Status=='pending':
                messages.info(req, 'Your Status is in pending')
                return redirect('user_login')
            else:
                messages.warning(req, 'verifyOTP...!')
                req.session['User_id'] = user_data.User_id
                return redirect('otp')
        else:
            messages.error(req, 'incorrect credentials...!')
            return redirect('user_login')
    return render(req,'main-login.html')
def admin_login(req):
    admin_name = 'admin@gmail.com'
    admin_pwd = 'admin'
    if req.method == 'POST':
        admin_n = req.POST.get('adminName')
        admin_p = req.POST.get('adminPwd')
        if (admin_n == admin_name and admin_p == admin_pwd):
            messages.success(req, 'You are logged in..')
            return redirect('admindashboard')
        else:
            messages.error(req, 'You are trying to loging with wrong details..')
            return redirect('admin_login')
    return render(req,'main-admin.html')
def register(req):
    if req.method == 'POST' :
        name = req.POST.get('username')
        age = req.POST.get('Age')
        password = req.POST.get('password')
        phone = req.POST.get('phone')
        email = req.POST.get('email')
        address = req.POST.get("address")
        image = req.FILES['image']
        print(name,age,password,phone,email,address,image)
        image = req.FILES['image']
        number = random.randint(1000,9999)
        
        print(number)
        try:
            user_data = User.objects.get(Email = email)
            messages.warning(req, 'Email was already registered, choose another email..!')
            return redirect("register")
        except:
            User.objects.create(Full_name = name, Image = image, Age = age, Password = password, Address = address, Email = email, Phone_Number = phone, Otp_Num = number)
            mail_message = f'Registration Successfully\n Your 4 digit Pin is below\n {number}'
            print(mail_message)
            send_mail("User Password", mail_message , settings.EMAIL_HOST_USER, [email])
            req.session['Email'] = email
            messages.success(req, 'Your account was created..')
            return redirect('otp')
    return render(req,'main-register.html')
def otp(req):
    user_id = req.session['Email']
    user_o = User.objects.get(Email = user_id)
    print(user_o.Otp_Num,'data otp')
    if req.method == 'POST':
        user_otp = req.POST.get('otp')
        u_otp = int(user_otp)
        if u_otp == user_o.Otp_Num:
            user_o.Otp_Status = 'verified'
            user_o.save()
            messages.success(req, 'OTP verification was Success. Now you can continue to login..!')
            return redirect('home')
        else:
            messages.error(req, 'OTP verification was Faild. You entered invalid OTP..!')
            return redirect('otp')
    return render(req,'main-otp.html')
def forgot_pwd(req):
    return render(req,'main-forgotpwd.html')
def about_us(req):
    return render(req,'main-about.html')
def contact_us(req):
    if req.method == 'POST':
        name = req.POST.get('name')
        email = req.POST.get('email')
        phone = req.POST.get('phone')
        address = req.POST.get('address')
        message = req.POST.get('message')
        print(name,email,message,phone,address, 'uuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
        User.objects.create(Full_name=name,Email=email,Message=message,Phone_Number=phone,Address=address)
        messages.success(req, 'Your message has been submitted successfully.')
        return redirect('contact_us') 
    return render(req,'main-contact.html')
