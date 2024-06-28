from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
from .models import *

# Create your views here.
def index(request):
    return render(request,'index.html')

def signup(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        
        password=request.POST['password']
        password2=request.POST['password2']

        if password==password2:      #checks if repeat password is equal to original password
            if User.objects.filter(email=email).exists():   #checks if the email entered already exists in database
                messages.info(request,'Email already exists')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():   #checks if the username entered already exists in database
                messages.info(request,'username already exists')
                return redirect('signup')
            else:
                user=User.objects.create_user(username=username,email=email,password=password)  #creates a user if all conditions are satisfied
                user.save();
                new_profile = Profile.objects.create(user=user, id_user=user.id)   #simultaneously creates a profile object
                new_profile.save();
                return redirect('signin')
        else:
            messages.info(request,'password is not same')
            return redirect('signup')
    else:        
        return render(request,'signup.html')

def signin(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']

        user=auth.authenticate(username=username,password=password)   #checks if the user already registered in database

        if user is not None:    #if user exists
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'credentials invalid')
            return redirect('signin')
    else:
        return render(request,'signin.html')