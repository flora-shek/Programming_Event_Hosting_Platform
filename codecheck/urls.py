from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name ="index"),
    path('register/', views.register, name='register'),
    path('verify/', views.verify_otp, name='verify'),
    path('forgotpass/', views.forgotpass, name='forgotpass'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
   
]