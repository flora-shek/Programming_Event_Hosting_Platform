from django.shortcuts import render,redirect
from datetime import datetime, timedelta,date
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse,JsonResponse
from .email import YagmailWrapper
from django.template import loader
from .models import UserModel,EventModel,ProblemModel,SubmissionModel
from werkzeug.security import generate_password_hash,check_password_hash
import random
import string
from textwrap import dedent
import hashlib
from django.contrib import messages
import pytz


TODAY = date.today()
def save_data(request):
   
    hash = UserModel.get_user("florashek24@gmail.com")['password']
    v = get_password(hash,"shek77shek77")
    return JsonResponse({"message": "User created", "id": str(v)})

def index(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        name = UserModel.get_user_id(user_id)[0]["name"]
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
        messages.success(request,f"Successfully logged out!")
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
def event_status(today,event):
    start_date = event['start_date'].date()
    end_date = event['end_date'].date()

    
    if today < start_date:
        event_status = "Upcoming"
    elif start_date <= today <= end_date:
        event_status = "Ongoing"
    else:
        event_status = "Finished"
    return event_status
def events(request):
   
    # Fetch all events initially
    events = EventModel.all_event()
   
    
    if request.method == 'POST':
        search_term = request.POST.get("esearch")
        if search_term:
            # Search events by the search term
            events = EventModel.search_event(search_term)
    for e in events:
        e['status'] = event_status(TODAY,e)
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
        e['status'] = event_status(TODAY,e)
    if TODAY > events[0]["registration_enddate"].date():
        disable = True
    else:
        disable = False

    context = {
        'event': events[0],
         'login':False,
         'disable': disable
        
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
        event_name = event[0]['name']
        mail = UserModel.get_user_id(int(u_id))
        email = mail[0]['name'] #key error

        if TODAY < event[0]['registration_startdate'].date():
            messages.error(request, "Registration for this event has not started yet.")
            return redirect('events')
        elif TODAY > event[0]['registration_enddate'].date():
            messages.error(request, "Registration for this event has already closed.")
            return redirect('events')
        
        if int(u_id) in event[0]["registrations"]:
            messages.warning(request, "You are already registered for this event.")
        else:
            # Add user to the registrations list
             EventModel.collection.update_one(
            {"event_id": int(event_id)},
            {"$addToSet": {"registrations": int(u_id)}}  
        )
 
             messages.success(request, "Successfully registered for the event!")
       
             yagmail = YagmailWrapper()
             subject = 'Event Registration Confirmed'
                

             body = dedent(f"""
                    Hello there,

                    You have been successfully registered for the event '{event_name}' from your account in Code Evaluator. 

                    If you need further assistance, feel free to reach out to our support team.

                    Best regards,
                    The Code Evaluator Team
                """)

                
            
             success = yagmail.send_email(email, subject, body)

        return redirect('events')  
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)
    
def dashboard(request):
    u_id = request.session.get("user_id")
    user_events = EventModel.get_user_events(int(u_id))
    for e in user_events:
        e['status'] = event_status(TODAY,e)
        if TODAY == e["start_date"].date() or( TODAY > e["start_date"].date() and TODAY < e["end_date"].date()) or TODAY == e["end_date"].date():
            e['notattend'] = False
        else:
           e['notattend'] = True
    p = False
    participation = EventModel.get_p_events(int(u_id))
    if len(participation)>0:
        p = True
    context = {
        'events': user_events,
        'login':True,
        'p':p,
       'parts':participation
    }
    
    return render(request, 'user_dashboard.html',context)

def code(request,event_id):
    user_id = request.session.get('user_id')
    event_problems =  ProblemModel.get_problems_id(event_id)
    
    if 'current_problem_index' not in request.session:
        request.session['current_problem_index'] = 0 
    current_index = request.session['current_problem_index']
    if current_index >= len(event_problems):
        EventModel.collection.update_one(
            {"event_id": int(event_id)},
            {"$addToSet": {"participations": int(user_id)}}  
        )
        del request.session['current_problem_index']
        messages.success(request, "Submitted Successfully")
        return redirect('index')
    
    problem = event_problems[current_index]

    if request.method == 'POST':
        user_solution = request.POST.get('editor')
       
        s_id = SubmissionModel.count()+1
        data = dict(
            submission_id= s_id,
            problem_id= problem["problem_id"],
            user_id=int(user_id),
            code= str(user_solution))
        SubmissionModel.delete(user_id,problem["problem_id"])
        if SubmissionModel.insert(data):
            request.session['current_problem_index'] += 1  
            return redirect('code', event_id=event_id) 

    return render(request, 'code.html', {'problem': problem})

def admin(request):
    u_id = request.session.get("user_id")
    user_events = EventModel.get_events(int(u_id))
    for e in user_events:
        e['status'] = event_status(TODAY,e)
    context = {
        'events': user_events,
        'login':True,
    }
    if request.method == 'POST':
        event_id = EventModel.count()+1
        user_id = request.session['user_id']
        name = request.POST.get('event_name')
        description =request.POST.get('event_description')
        registration_startdate =datetime.strptime(request.POST.get('event_rsdate'),"%Y-%m-%d")
        registration_enddate =datetime.strptime(request.POST.get('event_redate'),"%Y-%m-%d")
        event_startdate=datetime.strptime(request.POST.get('event_sdate'),"%Y-%m-%d")
        event_enddate =datetime.strptime(request.POST.get('event_edate'),"%Y-%m-%d")
        data = {
            "event_id":event_id,
            "user_id":int(user_id),
            "name": name,
            "description": description,
            "registration_startdate":registration_startdate,
            "registration_enddate":registration_enddate,
            "start_date": event_startdate,
            "end_date":event_enddate
        }
        if EventModel.create_event(data):
            messages.success(request, "Event created successfully.")
            redirect('admin')
        else:
            messages.error(request,"Unknown Error")
    return render(request,"admin.html",context)

def add_problem(request,event_id):
    if request.method == 'POST':
        problem_id = ProblemModel.count()+1
        event_id = event_id
        title = request.POST.get('problem_title')
        description=request.POST.get('problem_statement')
        input_format=request.POST.get('problem_op')
        output_format=request.POST.get('problem_ip')
        sample_input=request.POST.get('problem_sip')
        sample_output=request.POST.get('problem_sop')
        data={
            "problem_id":problem_id,
            "event_id":event_id,
            "title":title,
            "description":description,
            "input_format":input_format,
            "output_format": output_format,
            "sample_input":sample_input,
            "sample_output":sample_output
        }
        if ProblemModel.create(data):
            messages.success(request, "Problem created successfully.")
    return render(request,"add_problem.html")

def admin_event(request,event_id):
    event = EventModel.get_event_id(event_id)
    problems = ProblemModel.get_problems_id(event_id)
    evaluate = False
    event[0]['status'] = event_status(TODAY,event[0])
    if event[0]['status']=="Finished":
        evaluate = True
    context = {
        'event':event[0],
        "problems":problems,
        "login":True,
        "evaluate":evaluate
    }
    return render(request,'admin_event.html',context)

def delete_event(request,event_id):
    if EventModel.delete(event_id):
        messages.success(request,"Event Deleted Successfully")
        return redirect('admin')
    else:
        messages.success(request,"Unknown Error")
        return redirect('admin')
    
    