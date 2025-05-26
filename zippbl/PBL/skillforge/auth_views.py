from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django import forms
from django.contrib.auth.models import User

class ExtendedUserCreationForm(UserCreationForm):
    """Extended user creation form with email and name fields"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user

def register_view(request):
    """
    Handle user registration
    """
    try:
        if request.method == 'POST':
            form = ExtendedUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                # Try to authenticate and log in
                try:
                    user = authenticate(username=username, password=raw_password)
                    if user is not None:
                        login(request, user)
                        messages.success(request, f"Account created for {username}! You are now logged in.")
                        return redirect('home')
                    else:
                        messages.warning(request, "Account created, but automatic login failed. Please log in manually.")
                        return redirect('login')
                except Exception as e:
                    # Create account but don't log in automatically if there's an authentication error
                    messages.warning(request, "Account created, but automatic login failed. Please log in manually.")
                    return redirect('login')
            else:
                # Form has errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = ExtendedUserCreationForm()
        
        return render(request, 'minimal_register.html', {'form': form})
    except Exception as e:
        # Catch any unexpected errors
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        form = ExtendedUserCreationForm()
        return render(request, 'minimal_register.html', {'form': form})
