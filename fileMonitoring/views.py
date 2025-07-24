from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required

# --- Registration View ---
def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        create_user_with_profile(user, role='standard')  # safely defaults
        messages.success(request, 'Account created. You can now log in.')
        return redirect('login')

    return render(request, 'accounts/register.html')


# --- Login View ---
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            ActivityLog.objects.create(user=user, action='login')
            return redirect('dashboard')
        else:
            messages.warning(request, 'Invalid credentials.')

    return render(request, 'accounts/login.html')

@login_required
def dashboard(request):
    user = request.user

    recent_uploads = Document.objects.filter(uploaded_by=user, is_deleted=False).order_by('-uploaded_at')[:5]
    recent_activities = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5]

    return render(request, 'dashboard.html', {
        'recent_uploads': recent_uploads,
        'recent_activities': recent_activities,
    })

# --- Logout View ---
def logout_user(request):
    ActivityLog.objects.create(user=request.user, action='logout')
    logout(request)
    return redirect('login')
