from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
from .models import *
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url='signin')    #redirects the user to log in page if the user is not logged in
def index(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(request,'index.html',{'user_profile':user_profile})

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

                #log the user in after signup so that user can be redirected to settings page
                user_login = auth.authenticate(username=username,password=password)
                auth.login(request,user_login)

                new_profile = Profile.objects.create(user=user, id_user=user.id)   #simultaneously creates a profile object
                new_profile.save();
                return redirect('settings')
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

@login_required(login_url='signin')     
def logout(request):
    auth.logout(request)
    return redirect('/')

@login_required(login_url='signin')   
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method=='POST':

        if request.FILES.get('image')==None:
            image= user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image')!= None:
            image= request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('settings')
        
    return render(request,'setting.html',{'user_profile':user_profile})

@login_required(login_url='signin')  
def upload(request):
    if request.method=='POST':
        user = request.user.username
        image = request.FILES.get('post_img')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user,image=image,caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/') 

