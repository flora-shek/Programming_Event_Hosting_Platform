from django.shortcuts import render,redirect
from datetime import datetime, timedelta,timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse,JsonResponse
from .email import YagmailWrapper
from django.template import loader
from .models import UserModel,EventModel
from werkzeug.security import generate_password_hash,check_password_hash
import random
import string
from textwrap import dedent
import hashlib
from django.contrib import messages




def save_data(request):
   
    hash = UserModel.get_user("florashek24@gmail.com")['password']
    v = get_password(hash,"shek77shek77")
    return JsonResponse({"message": "User created", "id": str(v)})

def index(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        name = UserModel.get_user_id(user_id)["name"]
        messages.success(request,f"Welcome back! {name}")
        return render(request, 'home.html',{'login':True})
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
        user = UserModel.get_user(str(email))

        if user:
            try:
                yagmail = YagmailWrapper()
                subject = 'Password Reset Request'
                expiry_time = datetime.now() + timedelta(minutes=10)
                otp = generate_otp()

                body = dedent(f"""
                    Hello {user['name']},

                    We received a request to reset your password for your account in Code Evaluator. To reset your password, please use the following One-Time Password (OTP):

                    **{otp}**

                    This OTP will expire in 10 minutes. If you did not request a password reset, you can safely ignore this email. Your account will remain secure.

                    If you need further assistance, feel free to reach out to our support team.

                    Best regards,
                    The Code Evaluator Team
                """)

                otp_hash = hashlib.sha256(otp.encode()).hexdigest()
                request.session['otp_code'] = otp_hash
                request.session['otp_expiry'] = expiry_time.isoformat()
                request.session['mail']= email
                success = yagmail.send_email(email, subject, body)

                if success:
                    return render(request, 'forgot.html', {
                        "title": "Password Reset",
                        "content": "Enter your email address and we'll send you a link to reset your password.",
                        "output": "Email Successfully Sent!",
                        "theme": "success"
                    })
                else:
                    raise Exception("Email sending failed.")
            except Exception as e:
                print(f"Error: {e}")
                return render(request, 'forgot.html', {
                    "title": "Password Reset",
                    "content": "Enter your email address and we'll send you a link to reset your password.",
                    "output": "Oops, error sending email.",
                    "theme": "danger"
                })

        # Generic message to prevent user enumeration
        return render(request, 'forgot.html', {
            "title": "Password Reset",
            "content": "If the email exists, a password reset link will be sent.",
            "theme": "info"
        })

    return render(request, 'forgot.html', {
        "title": "Password Reset",
        "content": "Enter your email address and we'll send you a link to reset your password."
    })
@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        newpass =  request.POST.get('password')
        saved_otp = request.session.get('otp_code')
        otp_expiry = request.session.get('otp_expiry')
        email = request.session.get('mail')
        # Convert expiry time back to datetime
        if otp_expiry:
            otp_expiry = datetime.fromisoformat(otp_expiry)

        if saved_otp and otp_expiry and datetime.now() < otp_expiry:
            # Hash entered OTP for secure comparison
            entered_otp_hashed = hashlib.sha256(entered_otp.encode()).hexdigest()

            if entered_otp_hashed == saved_otp:
                # Clear session variables after successful verification
                request.session.pop('otp_code', None)
                request.session.pop('otp_expiry', None)
                hash = set_password(newpass)
                UserModel.update_user(str(email),{"password":str(hash)})
                return redirect('login')

            else:
                return render(request, 'forgot.html', {"title": "Verify OTP","content": "Enter the OTP received in your email to verify your identity.","output":'Invalid OTP. Please try again.',"theme": "danger"})
        else:
            
            return render(request, 'forgot.html', {"title": "Verify OTP","content": "Enter the OTP received in your email to verify your identity.","output": "OTP has expired or is invalid. Please request a new one.","theme": "danger"})

    return render(request, 'forgot.html', {
        "title": "Verify OTP",
        "content": "Enter the OTP received in your email to verify your identity."
    })

def events(request):
   
    # Fetch all events initially
    events = EventModel.all_event()
    current_time =  datetime.now(timezone.utc)
    
    if request.method == 'POST':
        search_term = request.POST.get("esearch")
        if search_term:
            # Search events by the search term
            events = EventModel.search_event(search_term)

    for e in events:
        e['start_date'] = datetime.strptime(e['start_date'], "%Y-%m-%dT%H:%M:%SZ")
        e['end_date'] = datetime.strptime(e['end_date'], "%Y-%m-%dT%H:%M:%SZ")
        
    context = {
        'events': events,
        'login':True,
        
    }

    return render(request, 'event.html', context)

def event_details(request,id):
    if request.method == 'POST':
        messages.success(request,"Successfully registered for event")
    events = EventModel.get_event_id(int(id))
    for e in events:
        e['start_date'] = datetime.strptime(e['start_date'], "%Y-%m-%dT%H:%M:%SZ")
        e['end_date'] = datetime.strptime(e['end_date'], "%Y-%m-%dT%H:%M:%SZ")
    context = {
        'event': events[0],
         'login':True,
        
    }
    return render(request, 'event_details.html', context)


def register_for_event(request, event_id):
    if request.method == "POST":
        # Ensure the user is logged in
        u_id = request.session.get("user_id")
        if not u_id:
            messages.error(request, "You must be logged in to register for an event.")
            return redirect('login')  

        # Get the event
        event = EventModel.get_event_id(int(event_id))
      
        if int(u_id) in event[0]["registrations"]:
            messages.warning(request, "You are already registered for this event.")
        else:
            # Add user to the registrations list
             EventModel.collection.update_one(
            {"event_id": int(event_id)},
            {"$addToSet": {"registrations": int(u_id)}}  # Ensures no duplicates
        )

             messages.success(request, "Successfully registered for the event!")

        return redirect('events')  # Redirect to the events page
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)
    
def dashboard(request):
    u_id = request.session.get("user_id")
    user_events = EventModel.get_user_events(int(u_id))
    context = {
        'events': user_events,
        'login':True,
    }

    return render(request, 'user_dashboard.html',context)