from django.shortcuts import render,redirect
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse,JsonResponse
from .email import YagmailWrapper
from django.template import loader
from .models import UserModel
from werkzeug.security import generate_password_hash,check_password_hash
import random
import string
def dashboard(request):
    return render(request, 'user_dashboard.html',{"role":True,"login":True})

def save_data(request):
   
    hash = UserModel.get_user("florashek24@gmail.com")['password']
    v = get_password(hash,"shek77shek77")
    return JsonResponse({"message": "User created", "id": str(v)})

def index(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        name = UserModel.get_user_id(user_id)["name"]
        role = UserModel.get_user_id(user_id)["role"] == 'event organizer'
        return render(request, 'home.html', {'username': name, 'message': 'Welcome back!','role' : role,'login':True })
    else:
        return redirect('login')  



@csrf_exempt
def register(request):
    if request.method == 'POST':
        now = datetime.now()

    
        user_id = UserModel.count_users() + 1
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        created_at = now.strftime("%Y-%m-%d")

 
        if UserModel.get_user(email):
            return render(request, 'register.html', {
                "output": "Email already exists. Please try a different one.",
                "theme": "danger"
            })

   
        hash = set_password(password)

     
        data = {
            "user_id": user_id,
            "name": str(name),
            "email": str(email),
            "password": str(hash),
            "role": str(role),
            "created_at": str(created_at)
        }

        
        UserModel.create_user(data)

        return render(request, 'register.html', {
            "output": "Successfully registered. Login to proceed!",
            "theme": "success",'login':False
        })

    
    return render(request, 'register.html', {"output": "", "theme": "",'login':False })

def set_password(password):
        g_password = generate_password_hash(password)
        return g_password

def get_password(hash,password):
        return check_password_hash(hash,password)


@csrf_exempt
def login(request): 
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        

        user = UserModel.get_user(str(email))
        
        if user:
            
            hash = user['password']
            
            
            if get_password(hash, str(password)):
                
                request.session['user_id'] = user['user_id']
                request.session.set_expiry(3600)
               
                return redirect('index')  
                
          
            return render(request, 'login.html', {"output": "Invalid email or password!", "theme": "danger"})
        
      
    return render(request, 'login.html', {"output": "", "theme": "",'login':False})
    
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login')

def generate_otp(length=6):
    characters = string.digits  
    otp = ''.join(random.choice(characters) for i in range(length))
    return otp

@csrf_exempt
def forgotpass(request):
     if request.method == 'POST':
          email = request.POST.get('email')
          yagmail = YagmailWrapper()
          user = UserModel.get_user(str(email))
          subject = 'password reset request'
          expiry_time = datetime.now() + timedelta(minutes=10)
          otp = generate_otp()
          body = f"""
    Hello {user.name},

    We received a request to reset your password for your account in Code evaluator. To reset your password, please use the following One-Time Password (OTP):

    **{otp}**

    This OTP will expire in 10 minutes. If you did not request a password reset, you can safely ignore this email. Your account will remain secure.

    If you need further assistance, feel free to reach out to our support team.

    Best regards,
    The Code evaluator Team
    """
          to = email
          user.otp_code = otp
          user.otp_expiry = expiry_time
          user.save()
   
          success = yagmail.send_email(to, subject, body)

          if success:
                return HttpResponse('Email sent successfully!')
          else:
                return HttpResponse('Error sending email.')
     return render(request,'forgot.html',{"title":"Password Reset",'content':"Enter your email address and we'll send you a link to reset your password."})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('otp_code')
        otp_expiry = request.session.get('otp_expiry')

        if saved_otp and otp_expiry and datetime.now() < otp_expiry:
            if entered_otp == saved_otp:
                messages.success(request, 'OTP verified successfully. You can now reset your password.')
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        else:
            messages.error(request, 'OTP has expired or is invalid. Please request a new one.')

    return render(request,'forgot.html',{"title":"Verification",'content':"Enter your OTP recieved from your email and enter your new password."})