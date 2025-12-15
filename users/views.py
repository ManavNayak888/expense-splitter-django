from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration Successful !')
            return redirect('dashboard')
        else:
            return render(request, 'users/register.html', {'form': form})
    else:
        form = UserCreationForm()
        return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data= request.POST)
        if form.is_valid():
            user= form.get_user()
            login(request, user)
            messages.success(request, f'Welcome Back, {user.username}')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
        return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

