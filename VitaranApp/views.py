import imp
from queue import Empty
from sre_parse import FLAGS
from django.shortcuts import render,HttpResponse,redirect
import math,random
import smtplib
from django.urls import reverse
from VitaranApp.encryption_util import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from .forms import CreateUserForm
from .models import Bill, Profile, User
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib import messages
import pdfkit
from django.template import loader
from django.contrib import sessions
from django.http import JsonResponse
from decouple import config
from .resources import BillResources
from tablib import Dataset
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
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

def logout(request):
    request.session.flush()
    return redirect('/')

def generate_otp():
        digits = "0123456789"
        otp = ""
        for i in range(6):
            otp += digits[math.floor(random.random()*10)]
        return otp

def send_otp(request,Email, Employee_ID):
    server = smtplib.SMTP(config('EMAIL_SERVER'),config('EMAIL_PORT',cast=int))
    server.starttls()
    email_from = config('EMAIL_FROM')
    email_to = decrypt(Email)
    server.login(email_from,config('EMAIL_PASSWORD'))
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
            return redirect(choose, Employee_ID = Employee_ID, otp = otp)
         else:
            flag=False
            return render(request,'otp.html',{'flag':flag})
    return render(request,'otp.html',{'flag':flag})

#------

def index(request):
    return render(request,'index.html')

@login_required(login_url='loginsuperuser')
def indexsuperuser(request):
    current_user = request.user
    msg = "Welcome " + current_user.first_name +" " + current_user.last_name
    return render(request, 'indexsuperuser.html', {'msg':msg})

def loginsuperuser(request):
    if request.method == 'POST':
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username = username, password = password)

        if user is not None:
            auth_login(request, user)
            return redirect(indexsuperuser)
        else:
            msg = "Bad Credentials !!!"
            return render(request, 'loginsuperuser.html', {'msg': msg})
    return render(request, 'loginsuperuser.html')

def logoutsuperuser(request):
    logout(request)
    msg = "Logged out successfully !!!"
    return render(request, 'index.html')

@login_required(login_url='loginsuperuser')
def registersuperuser(request):
    form = CreateUserForm()
    if request.method =='POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.instance.is_staff = True
            form.instance.is_superuser = True
            form.save()
            msg = "Admin Created Successfully !!!"
            return render(request, 'indexsuperuser.html', {'msg':msg})
    return render(request,'registersuperuser.html', {'form':form})

def choose(request, Employee_ID, otp):
    encryptedID = Employee_ID
    EmployeeID = decrypt(Employee_ID)
    data = Profile.objects.get(Employee_ID = EmployeeID)
    return render(request, 'choose.html', {'data':data, 'encryptedID':encryptedID})

def viewannually(request,year,encryptedID):
    Employee_ID=decrypt(encryptedID)
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
    size = int((len(bill)))
    if size > int(0):
        print(bill)
        total_amt=int(0)
        total_units = int(0)
        for i in bill:
              total_amt += int(i.payable_amount)
              total_units += int((int(i.current_units) - int(i.previous_units)))
        return render(request,'viewannually.html',{'user':user,'year':year,'total_amt':total_amt,'total_units':total_units})
    else:
        msg = "No Bills Found !!!"
        return redirect(annually, encryptedID)
        # return render(request, 'annually.html', {'msg':msg})

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
    print(bill)
    if bill is not None:
        total_unit = bill.unitP1 + bill.unitP2 + bill.unitP3 + bill.unitP4 + bill.unitP5
        return render(request,'viewmonthly.html',{'user':user,'bill':bill,'total_unit':total_unit})
    else:
        return redirect(monthly, encryptedID)
        # msg = "No Bills Found!!!"
        # ins = str(encryptedID)
        # print(type(ins))
        # return reverse('monthly',encryptedID)

        # return render(request, 'monthly.html', {'user': user , 'bill':bill, 'msg':msg})

@login_required(login_url='loginsuperuser')
def viewalluser(request):
    alluser = Profile.objects.all()
    return render(request, 'viewalluser.html', {'alluser':alluser})

@login_required(login_url='loginsuperuser')
def Excel(request):
    flag = False
    if request.method == "POST":
        month = request.POST.get('month', "")
        year = request.POST.get('year', "")
        unitP1 = int(request.POST.get('unitP1', ""))
        unitP2 = int(request.POST.get('unitP2', ""))
        unitP3 = int(request.POST.get('unitP3', ""))
        unitP4 = int(request.POST.get('unitP4', ""))
        unitP5 = int(request.POST.get('unitP5', ""))
        rateP1 = float(request.POST.get('rateP1', ""))
        rateP2 = float(request.POST.get('rateP2', ""))
        rateP3 = float(request.POST.get('rateP3', ""))
        rateP4 = float(request.POST.get('rateP4', ""))
        rateP5 = float(request.POST.get('rateP5', ""))
        rateP6 = float(request.POST.get('rateP6', ""))
        designation = request.POST.get('designation', "")
        bill_resource = BillResources()
        dataset = Dataset()
        new_bill = request.FILES['excel']
        
        if not new_bill.name.endswith('xlsx'):
            flag = True
            msg = "Worng Format....Please upload an excel file"
            return render(request, 'Excel.html', {'msg':msg, 'flag':flag})
        imported_data = dataset.load(new_bill.read(), format='xlsx')
        # print(imported_data)
        for data in imported_data:
            if data[5] is None or data[7] is None:
                continue
            units_consumed = int(int(data[7]) - int(data[5]))
            unit1 = int(0)
            unit2 = int(0)
            unit3 = int(0)
            unit4 = int(0)
            unit5 = int(0)
            unit6 = int(0)
            for i in data:
                print(i)
            if units_consumed > unitP1:
                unit1 = unitP1
            else:
                unit1 = units_consumed
            if units_consumed <= unitP1:
                unit2 = int(0)
            elif unitP1 < units_consumed and units_consumed <= (unitP1+unitP2):
                unit2 = int(units_consumed- unitP1)
            else :
                # units_consumed > (unitP1+unitP2)
                unit2 = int(unitP2)
            if units_consumed <= unitP1 + unitP2:
                unit3 = int(0)
            elif unitP1+unitP2 < units_consumed and units_consumed <= (unitP1+unitP2+unitP3):
                unit3 = int(units_consumed- (unitP1+unitP2))
            else :
                unit3 = int(unitP3)
            if units_consumed <= unitP1 + unitP2 + unitP3:
                unit4 = int(0)
            elif unitP1+unitP2+unitP3 < units_consumed and units_consumed <= (unitP1+unitP2+unitP3+unitP4):
                unit4 = int(units_consumed- (unitP1+unitP2+unitP3))
            else :
                unit4 = int(unitP4)
            if units_consumed <= unitP1 + unitP2 + unitP3 + unitP4:
                unit5 = int(0)
            elif unitP1+unitP2+unitP3+unitP4 < units_consumed and units_consumed <= (unitP1+unitP2+unitP3+unitP4+unitP5):
                unit5 = int(units_consumed- (unitP1+unitP2+unitP3+unitP4))
            else :
                unit5 = int(unitP5)


            if units_consumed <= (unitP1+unitP2+unitP3+unitP4+unitP5):
                unit6 = int(0)
            else:
                unit6 = units_consumed - (unitP1+unitP2+unitP3+unitP4+unitP5)
            amount = rateP1*unit1 + rateP2*unit2 + rateP3*unit3 + rateP3*unit3 + rateP4*unit4 + rateP5*unit5 + rateP6*unit6 + int(data[6])
            ins = Bill(quarter_no = data[0], Name=  data[1] ,meter_no = data[2],sanction_load= data[3],Employee_ID= data[4], previous_units= data[5],KVA_charge= float(data[6]),current_units= data[7], net_billed_unit = units_consumed, month = month, year = year, rateP1 = rateP1, rateP2 = rateP2, rateP3= rateP3, rateP4 = rateP4, rateP5 = rateP5, rateP6 = rateP6, unitP1 = unitP1, unitP2 = unitP2, unitP3 = unitP3 , unitP4 = unitP4, unitP5 = unitP5, payable_amount = amount)
            ins.save()
        data = Bill.objects.filter(month = month, year = year).values_list()
        return render(request, 'receipt.html', {'imported_data':data, 'designation':designation})
    return render(request, 'Excel.html')

@login_required(login_url='loginsuperuser')
def adduser(request):
    if request.method == "POST":
        Name = request.POST.get('Name', "")
        Employee_ID = request.POST.get('Employee_ID', "")
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
            ins = Profile(Name = Name, Employee_ID = Employee_ID, Email = Email, quarter_no = quarter_no, meter_no = meter_no, OTP = OTP)
            ins.save()
            msg = "Resident added Successfully !!!"
            return render(request, 'indexsuperuser.html', {'msg':msg})
        else :
            msg = "Resident already Exists"
            return render(request,'adduser.html', {'msg': msg})
    return render(request,'adduser.html')

@login_required(login_url='loginsuperuser')
def edituser(request):
    if request.method == 'POST':
        flag = request.POST.get('flag', "")
        if flag == "small":
            Employee_ID = request.POST.get('Employee_ID', "")
            user = None
            userExist = True
            try:
                user = Profile.objects.get(Employee_ID = Employee_ID)
            except Profile.DoesNotExist:
                user = None
                userExist = False
            return render(request, 'edituser.html', {'userExist':userExist, 'user':user})
        else:
            Name = request.POST.get('Name', "")
            Employee_ID = request.POST.get('Employee_ID', "")
            Email = request.POST.get('Email', "")
            quarter_no = request.POST.get('quarter_no', "")
            meter_no = request.POST.get('meter_no', "")
            user = Profile.objects.get(Employee_ID = Employee_ID)

            user.Name = Name
            user.Email = Email
            user.quarter_no = quarter_no
            user.meter_no = meter_no
            user.save()
            msg = "Resident Updated Successfully !!!"
            return render(request, 'indexsuperuser.html', {'msg':msg})
    return render(request, 'edituser.html')

@login_required(login_url='loginsuperuser')
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
        msg = "Resident deleted Successfully !!!"
        return render(request, 'indexsuperuser.html', {'msg':msg})
    return render(request, 'deleteuser.html')

@login_required(login_url='loginsuperuser')
def deleteSuperUser(request):
    success = False
    if request.method == "POST":
        username = request.POST.get("username", "")
        user = None
        userExist = True
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            user = None
        if user is None:
            userExist = False
            return render(request, 'deletesuperuser.html', {'userExist':userExist})
        success = True
        User.objects.filter(username = username).delete()
        msg = "Admin Deleted Successfully !!!"
        return render(request, 'indexsuperuser.html', {'msg':msg})
    return render(request, 'deletesuperuser.html')

@login_required(login_url='')
def deletebill(request):
    if request.method == 'POST':
        month = request.POST.get("month", "")
        year = request.POST.get("year", "")
        bill = Bill.objects.filter(month = month, year = year)
        bill.delete()
        msg = "All Bills of All Residents of " + month +" has been deleted"
        return render(request, 'indexsuperuser.html', {'msg':msg})
    return render(request, 'deletebill.html')

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

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get("email", "")
        user = None
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            user = None
        if user is not None :
            server = smtplib.SMTP(config('EMAIL_SERVER'),config('EMAIL_PORT',cast=int))
            server.starttls()
            email_from = config('EMAIL_FROM')
            email_to = email
            server.login(email_from,config('EMAIL_PASSWORD'))
            email_template_name = "password_reset_email.txt"
            c = {
            "email":user.email,
            'domain':'127.0.0.1:8000',
            'site_name': 'Website',
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            'token': default_token_generator.make_token(user),
            'protocol': 'http',
            }
            email = render_to_string(email_template_name, c)
            server.sendmail(email_from,email_to,email)
            server.quit()
            return redirect ("/password_reset/done/")
        else:
            msg = "No user with entered Email Id found !!!"
            return render(request, 'password_reset.html', {'msg':msg})
    return render(request, 'password_reset.html')

@login_required(login_url='loginsuperuser')
def previousbills(request):
    if request.method == "POST":
        month = request.POST.get('month',"")
        year = request.POST.get('year',"")
        designation = request.POST.get('designation',"")
        imported_data = None
        try:
            imported_data = Bill.objects.filter(year = year, month = month).values_list()
        except Bill.DoesNotExist:
            imported_data = None
        size = int((len(imported_data)))
        print(size)
        if size == int(0):
            msg = "No Bills Found!!!"
            return render(request,'previousbills.html',{'msg':msg})
        else:
            return render(request,'receipt.html',{'imported_data':imported_data,'designation':designation,'month':month,'year':year})
    return render(request,'previousbills.html')




@login_required(login_url='loginsuperuser')
def adduserExcel(request):
    flag = False
    if request.method == "POST":
        name = request.POST.get("Name", "")
        Employee_ID = request.POST.get("Employee_ID", "")
        email = request.POST.get("email", "")
        quarter_no = request.POST.get("quarter_no", "")
        meter_no = request.POST.get("meter_no", "")
        # bill_resource = BillResources()
        dataset = Dataset()
        new_bill = request.FILES['excel']
        
        if not new_bill.name.endswith('xlsx'):
            flag = True
            msg = "Worng Format....Please upload an excel file"
            return render(request, 'adduserExcel.html', {'msg':msg, 'flag':flag})
        imported_data = dataset.load(new_bill.read(), format='xlsx')
        # print(imported_data)
        for data in imported_data:
            
            ins = Profile(Name = data[0], Employee_ID=  data[1] ,Email = data[2],quarter_no= data[3], meter_no= data[4])
            ins.save()
    return render(request, 'adduserExcel.html')