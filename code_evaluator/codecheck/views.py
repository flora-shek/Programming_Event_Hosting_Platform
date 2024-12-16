from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse,JsonResponse
from django.template import loader
from .models import UserModel
from werkzeug.security import generate_password_hash,check_password_hash
'''def save_data(request):
   
    user_id = UserModel.list_users()
    return JsonResponse({"message": "User created", "id": str(user_id)})'''

def index(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

def register(request):
    template = loader.get_template('register.html')
    return HttpResponse(template.render())

@csrf_exempt
def register_user(request):
    now = datetime.now()
    if request.method == 'POST':
        user_id = (UserModel.count_users() + 1)
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        created_at =  now.strftime("%Y-%m-%d")
        hash = set_password(password)
        data = {
             "user_id": user_id,
             "name": str(name),
             "email": str(email),
             'password' : str(hash),
             "role": str(role),
             "created_at":str(created_at)
        }
        user = UserModel.create_user(data)

        return JsonResponse({"message": "User created", "id": str(user)})
    
    return HttpResponse("<h1>hi</h1>")

def set_password(password):
        g_password = generate_password_hash(password)
        return g_password

def get_password(password):
        return check_password_hash(password,password)
def login(request):
    template = loader.get_template('login.html')
    return HttpResponse(template.render())



    
