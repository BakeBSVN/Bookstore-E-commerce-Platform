from django.urls import path, include
from . import views
from bookshop.views import index
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('account/register', views.register, name='register'),
    path('account/login', views.login, name='login'),
    path('profile', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
]
