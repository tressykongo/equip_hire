
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm
from .models import Profile


def register(request):
    form = RegistrationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully.')
            return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={'role': 'RENTER'}
            )

            if profile.role == 'OWNER':
                return redirect('owner_dashboard')

            return redirect('renter_dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


@login_required
def renter_dashboard(request):
    return render(request, 'accounts/renter_dashboard.html')


@login_required
def owner_dashboard(request):
    return render(request, 'accounts/owner_dashboard.html')
def user_logout(request):
    logout(request)
    return redirect('login')
