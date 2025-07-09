from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from secrets import compare_digest
from django.core.mail import EmailMessage, send_mail
from django.utils.encoding import force_bytes, force_str


# Create your views here.

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        #check password
        if compare_digest(password, confirm_password):
            #check username
            if User.objects.filter(username=username).exists():
                messages.error(request, "That username is taken")
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, "That email is being used.")
                    return redirect('register')
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    messages.success(request, 'You are now registered and can login in')
                    return redirect('login')
        else:
            messages.error(request, "Password do not match.")
            return redirect('register')
    else:
        return render(request, 'users/registration.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are Now Logged in')
            return redirect('index')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('login')
    else:
        return render(request, 'users/login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def profile(request):
    return render(request, 'users/profile.html')
