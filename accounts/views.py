from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm


def register(request):
    """
    User registration view that creates a new user account.
    """
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Account created for {username}! You are now logged in.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """
    User profile view that displays user information and adoption applications.
    Requires user to be logged in.
    """
    # Get user's adoption applications
    adoption_applications = request.user.adoption_applications.all()
    context = {
        'adoption_applications': adoption_applications
    }
    return render(request, 'accounts/profile.html', context)
