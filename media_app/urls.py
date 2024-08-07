from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('signup/',views.signup,name='signup'),
    path('signin/',views.signin,name='signin'),
    path('logout/',views.logout,name='logout'),
    path('settings/',views.settings,name='settings'),
    path('upload/',views.upload,name='upload'),
    path('follow/',views.follow,name='follow'),
    path('likepost/',views.likepost,name='likepost'),
    path('profile/<str:username>',views.profile,name='profile'),
    path('search/',views.search,name="search")
]