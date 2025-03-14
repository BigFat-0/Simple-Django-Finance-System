# register/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('payapp:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('payapp:home')
    return render(request, 'register/login.html')

def user_logout(request):
    logout(request)
    return redirect('register:login')