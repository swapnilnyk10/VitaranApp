from pickle import FALSE
from queue import Empty
from django.shortcuts import render,HttpResponse,redirect
from .forms import Register
import math,random
import smtplib
from VitaranApp.encryption_util import *
from django.contrib.auth.decorators import login_required
from .models import Bill, Profile, User
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib import messages
import pdfkit
from django.template import loader
from django.contrib import sessions
from django.http import JsonResponse
# Create your views here.

def login(request):
    flag = False
    if request.method == "POST":
        Employee_ID = request.POST.get("Employee_ID")
        check = Profile.objects.filter(Employee_ID = Employee_ID).first()

        if check is None:
            flag = True
        #   return JsonResponse({'success':False},safe=False)
            return render(request,'login.html',{'flag':flag})
        else:
          data = Profile.objects.get(Employee_ID = Employee_ID)
          Email = data.Email
          messages.success(request,f'Your OTP has been sent! Please verify to enter the dashboard!')
          e = encrypt(Email)
          EmployeeID = encrypt(Employee_ID)
          return redirect(send_otp,Email = e, Employee_ID = EmployeeID)
    return render(request,'login.html',{'flag':flag})

def generate_otp():
        digits = "0123456789"
        otp = ""
        for i in range(4):
            otp += digits[math.floor(random.random()*10)]
        return otp

def send_otp(request,Email, Employee_ID):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    email_from = 'pandey.sachin0611@gmail.com'
    email_to = decrypt(Email)
    server.login(email_from,'coytpungzeirenkz')
    o=encrypt(generate_otp())
    email_message = MIMEMultipart()
    email_message['From'] = email_from
    email_message['To'] = email_to
    email_message['Subject'] = f'OTP Request'
    html = 'Your OTP for MNNIT VITARAN is'+' '+'<strong>'+decrypt(o)+'</strong>'+'.'+'<br><br><i>Please do not share this <strong>OTP</strong>. <br> This Email is auto generated and replies are not supported.</i>'
    email_message.attach(MIMEText(html, "html"))
    email_string = email_message.as_string()
    server.sendmail(email_from,email_to,email_string)
    server.quit()
    return redirect(check_otp,otp = o, Employee_ID = Employee_ID)
def check_otp(request,otp,Employee_ID):
    flag=True
    if request.method == "POST":
         otp_filled = request.POST.get("otp")
         
         if otp_filled == decrypt(otp):
            request.session['userLogin'] = True
            return redirect(choose, Employee_ID = Employee_ID)
         else:
            flag=False
            return render(request,'otp.html',{'flag':flag})
    return render(request,'otp.html',{'flag':flag})

# ------

def index(request):
    return render(request,'index.html')

def indexsuperuser(request,username):
    username = decrypt(username)
    data = User.objects.get(username = username)
    if data is None:
        msg = "Login first to view this page"
        return render(request, 'indexsuperuser.html',{'msg':msg})
    else:
        return render(request, 'indexsuperuser.html')

def loginsuperuser(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        data = User.objects.get(username = username)
        if data.check_password(password):
            username = encrypt(username)
            return redirect(indexsuperuser, username = username)
        else:
            msg = "Invalid Username"
            return render(request,'loginsuperuser.html', {'msg': msg})
    return render(request, 'loginsuperuser.html')

def registersuperuser(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        user = None
        userExist = False
        samePassword = True
        
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            user = None
        if user is not None : 
            userExist = True
            
            return render(request,'registersuperuser.html',{'userExist':userExist, 'samePassword' : samePassword})
        if password1 != password2 :
            samePassword = False
            return render(request,'registersuperuser.html',{'userExist':userExist, 'samePassword' : samePassword})
                
        is_staff = True
        is_active = True
        is_superuser = True
        ins = User(first_name = first_name,last_name = last_name, username = username, email = email, password =password1, is_staff = is_staff, is_active = is_active, is_superuser = is_superuser )
        ins.save()
        # user = User.objects.create_user(first_name = first_name,last_name = last_name, username = username, email = email, password1 =password1, password2 = password2, is_staff = is_staff, is_active = is_active, is_superuser = is_superuser )
        # user.save()
        return render(request,'registersuperuser.html',{'userExist':userExist, 'samePassword' : samePassword})
    return render(request,'registersuperuser.html')

def choose(request, Employee_ID):
    encryptedID = Employee_ID
    EmployeeID = decrypt(Employee_ID)
    data = Profile.objects.get(Employee_ID = EmployeeID)
    return render(request, 'choose.html', {'data':data, 'encryptedID':encryptedID})

def viewannually(request,year,encryptedID):
    Employee_ID =decrypt(encryptedID)
    user = None
    try:
        user = Profile.objects.get(Employee_ID = Employee_ID)
    except Profile.DoesNotExist:
        user = None
    bill = None
    try:
        bill = Bill.objects.filter(Employee_ID = Employee_ID,  year = year)
    except Bill.DoesNotExist:
        bill = None
    if bill.exists():
        total_units = int(0)
        total_net = int(0)
        total_payable = int(0)
        for i in bill:
            total_units += int(i.current_units) - int(i.previous_units)
            total_net += i.net_billed_amount
            total_payable += i.payable_amount
        # return render(request, 'viewannually.html', { 'user': user ,'year':year, 'total_units':total_units, 'total_net':total_net, 'total_payable': total_payable})
    
        # below code is for pdf -------->

        template = loader.get_template('viewannually.html')
        html = template.render({ 'user': user ,'year':year, 'total_units':total_units, 'total_net':total_net, 'total_payable': total_payable})
        options = {
            'page-size':'Letter',
            'encoding' : "UTF-8"
        }
        pdf = pdfkit.from_string(html,False,options)
        response = HttpResponse(pdf,content_type = 'application/pdf')
        response['Content-Diposition'] = 'attachment'
        filename = "Bill.pdf"
        return response
    else :
        msg = "No Bills found !!!"
        return render(request, 'viewannually.html', {'msg':msg})

def viewmonthly(request,month,year,encryptedID):
    Employee_ID =decrypt(encryptedID)
    user = None
    try:
        user = Profile.objects.get(Employee_ID = Employee_ID)
    except Profile.DoesNotExist:
        user = None
    bill = None
    try:
        bill = Bill.objects.get(Employee_ID = Employee_ID,  year = year, month = month)
    except Bill.DoesNotExist:
        bill = None

    # below code is for pdf -------->
        
    template = loader.get_template('viewmonthly.html')
    html = template.render({ 'user': user , 'bill':bill})
    options = {
        'page-size':'Letter',
        'encoding' : "UTF-8"
    }
    if bill is None:
       return render(request, 'viewmonthly.html', {'user': user , 'bill':bill})
    pdf = pdfkit.from_string(html,False,options)
    response = HttpResponse(pdf,content_type = 'application/pdf')
    response['Content-Diposition'] = 'attachment'
    filename = "Bill.pdf"
    return response
    # return render(request, 'viewmonthly.html', {'user': user , 'bill':bill})

def viewalluser(request):
    alluser = Profile.objects.all()
    return render(request, 'viewalluser.html', {'alluser':alluser})

def addbill(request):
    if request.method == "POST":      
        Employee_ID = request.POST.get('Employee_ID', "")
        month = request.POST.get('month', "")
        year = request.POST.get('year', "")
        tariff = request.POST.get('tariff', "")
        previous_units = request.POST.get('previous_units', "")
        current_units = request.POST.get('current_units', "")
        consumed_units = int(current_units) - int(previous_units)
        net_billed_amount = int(tariff) * int(consumed_units)
        payable_amount = net_billed_amount - 100
        ins = Bill(Employee_ID = Employee_ID, month = month, year = year, tariff = tariff, previous_units = previous_units, current_units = current_units, net_billed_amount = net_billed_amount, payable_amount = payable_amount)
        ins.save()
    return render(request,'addbill.html')

def adduser(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name', "")
        last_name = request.POST.get('last_name', "")
        Employee_ID = request.POST.get('Employee_ID', "")
        Phone = request.POST.get('Phone', "")
        Email = request.POST.get('Email', "")
        quarter_no = request.POST.get('quarter_no', "")
        meter_no = request.POST.get('meter_no', "")
        OTP = str(random.randint(1000,9999))
        
        user = None
        try:
            user = Profile.objects.get(Employee_ID = Employee_ID)
        except Profile.DoesNotExist:
            user = None

        if user is None:    
            ins = Profile(first_name = first_name, last_name = last_name, Employee_ID = Employee_ID, Phone = Phone, Email = Email, quarter_no = quarter_no, meter_no = meter_no, OTP = OTP)
            ins.save()
        else :
            msg = "user already Exists"
            return render(request,'adduser.html', {'msg': msg})
    return render(request,'adduser.html')

def deleteuser(request):
    success = False
    if request.method == "POST":
        Employee_ID = request.POST.get("Employee_ID", "")
        user = None
        userExist = True
        try:
            user = Profile.objects.get(Employee_ID = Employee_ID)
        except Profile.DoesNotExist:
            user = None
        if user is None:
            userExist = False
            return render(request, 'deleteuser.html', {'userExist':userExist})
        success = True
        Profile.objects.filter(Employee_ID = Employee_ID).delete()
        return render(request, 'deleteuser.html', {'success':success})
    return render(request, 'deleteuser.html')

def annually(request, encryptedID):
    if request.method == "POST":
        year = request.POST.get('year', "")
        return redirect(viewannually,year,encryptedID)
    return render(request, 'annually.html')

def monthly(request, encryptedID):
    if request.method == "POST":
        year = request.POST.get('year', "")
        month = request.POST.get('month', "")
        return redirect(viewmonthly, month,year,encryptedID)
    return render(request, 'monthly.html')