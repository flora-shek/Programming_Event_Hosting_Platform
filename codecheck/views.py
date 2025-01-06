from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse,JsonResponse
from django.template import loader
from .models import UserModel
from werkzeug.security import generate_password_hash,check_password_hash

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

def forgotpass(request):
     return render(request,'forgot.html')