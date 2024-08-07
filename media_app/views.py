from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
from .models import *
from django.contrib.auth.decorators import login_required
import random

# Create your views here.
@login_required(login_url='signin')    #redirects the user to log in page if the user is not logged in
def index(request):
    user_profile = Profile.objects.get(user=request.user)
    #to customize the post feed so that user can see only posts of users he is following
    user_following_list = []
    

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)


    
    feed_lists = Post.objects.filter(user__in=user_following_list)

    #random user suggestions
    all_users = User.objects.exclude(username=request.user.username)  #get all the users except current user
    user_already_follows = User.objects.filter(username__in=user_following_list)
    already_following_list =[]
    for users in user_already_follows:
        already_following_list.append(users.username)

    new_suggestion_list = all_users.exclude(username__in=already_following_list)

    final_suggestion_list = list(new_suggestion_list)
    random.shuffle(final_suggestion_list)     #to display random user suggestion each time the page is reloaded

    final_profile_suggestions = Profile.objects.filter(user__in=final_suggestion_list)[:4]
    
    return render(request,'index.html',{'user_profile':user_profile,'posts':feed_lists,'final_profile_suggestions':final_profile_suggestions})

@login_required(login_url='signin')
def likepost(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    #to check whether the user has already liked the particular post
    like_filter = LikePost.objects.filter(post_id=post_id,username=username).first()

    #if user has liked the post
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id,username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes +1  #increments no of likes 
        post.save()
        return redirect('/')
    else:                               #if user unlikes the post i.e if he has already liked it
        like_filter.delete()
        post.no_of_likes = post.no_of_likes -1
        post.save()
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    username_profile_list = []

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)  #This query performs a case-insensitive search for substrings within the username field.

        username_profile =[]
        

        for users in username_object:
            username_profile.append(users.id)

        username_profile_list = Profile.objects.filter(id_user__in=username_profile)

    return render(request,'search.html',{'user_profile': user_profile,'username_profile_list':username_profile_list})

@login_required(login_url='signin')
def profile(request,username):
    user_object = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=username)
    no_of_posts = len(user_posts)

    follower = request.user.username
    user=username

    #to change the button text to follow or unfollow depending on whether user is already following or not
    if FollowersCount.objects.filter(follower=follower,user=user).first():
        button_text='Unfollow'
    else:
        button_text='Follow'
    user_following = len(FollowersCount.objects.filter(follower=username))
    user_followers = len(FollowersCount.objects.filter(user=username))

    context = {
        'user_object':user_object,
        'user_profile':user_profile,
        'user_posts':user_posts,
        'no_of_posts':no_of_posts,
        'button_text':button_text,
        'user_following':user_following,
        'user_followers':user_followers
    }
    return render(request,'profile.html',context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        #to check whether the follower is already following the user
        if FollowersCount.objects.filter(follower=follower,user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')

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

