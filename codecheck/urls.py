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
    path('events/', views.events, name='events'),
    path('events/<str:id>', views.event_details, name='event_details'),
     path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    
   
]