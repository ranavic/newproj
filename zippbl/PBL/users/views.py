from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DetailView, ListView
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User, UserPreference
from .serializers import UserSerializer, UserPreferenceSerializer

# API Views
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Students can only see their own profile
        # Instructors can see their own profile and their students
        # Admins can see all profiles
        user = self.request.user
        if user.is_staff or getattr(user, 'is_admin_user', False):
            return User.objects.all()
        elif getattr(user, 'is_instructor', False):
            # In the simplified version, instructors just see themselves
            # In full implementation, they would see their students too
            try:
                # Attempt to get instructor's courses if that relationship exists
                if hasattr(user, 'instructor_courses'):
                    student_ids = user.instructor_courses.values_list('enrolled_students__id', flat=True)
                    return User.objects.filter(id__in=list(student_ids) + [user.id])
            except Exception:
                pass
            # Fallback to just showing the instructor their own profile
            return User.objects.filter(id=user.id)
        else:  # student
            return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get the current user's profile
        """
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user preferences
    """
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own preferences
        # Admins can see all preferences
        user = self.request.user
        if user.is_admin_user or user.is_staff:
            return UserPreference.objects.all()
        else:
            return UserPreference.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """
        Get the current user's preferences
        """
        try:
            preferences = UserPreference.objects.get(user=request.user)
            serializer = UserPreferenceSerializer(preferences, context={'request': request})
            return Response(serializer.data)
        except UserPreference.DoesNotExist:
            # Create default preferences if they don't exist
            preferences = UserPreference.objects.create(user=request.user)
            serializer = UserPreferenceSerializer(preferences, context={'request': request})
            return Response(serializer.data)

# Template Views
def register(request):
    """
    User registration view
    """
    if request.method == 'POST':
        # Process registration form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type', 'student')
        
        # Basic validation
        if password != password2:
            messages.error(request, _('Passwords do not match.'))
            return render(request, 'users/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, _('Username already exists.'))
            return render(request, 'users/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, _('Email already exists.'))
            return render(request, 'users/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type
        )
        
        # Create default preferences
        UserPreference.objects.create(user=user)
        
        # Log user in
        login(request, user)
        messages.success(request, _('Registration successful. Welcome to SkillForge!'))
        return redirect('dashboard')
    
    return render(request, 'users/register.html')

def user_login(request):
    """
    User login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, _('Login successful.'))
            return redirect('dashboard')
        else:
            messages.error(request, _('Invalid username or password.'))
    
    return render(request, 'users/login.html')

def user_logout(request):
    """
    User logout view
    """
    logout(request)
    messages.success(request, _('Logout successful.'))
    return redirect('home')

@login_required
def profile(request):
    """
    User profile view
    """
    user = request.user
    try:
        preferences = user.preferences
    except UserPreference.DoesNotExist:
        preferences = UserPreference.objects.create(user=user)
    
    return render(request, 'users/profile.html', {
        'user': user,
        'preferences': preferences
    })

class ProfileUpdateView(UpdateView):
    """
    View for updating user profile
    """
    model = User
    fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture', 
              'date_of_birth', 'phone_number', 'address', 'preferred_language',
              'linkedin_profile', 'github_profile', 'website']
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully.'))
        return super().form_valid(form)

class PreferenceUpdateView(UpdateView):
    """
    View for updating user preferences
    """
    model = UserPreference
    fields = ['learning_pace', 'preferred_content_type', 'notification_preferences',
              'study_reminder_time', 'visual_preference', 'auditory_preference',
              'reading_preference', 'kinesthetic_preference']
    template_name = 'users/preferences_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        try:
            return self.request.user.preferences
        except UserPreference.DoesNotExist:
            return UserPreference.objects.create(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, _('Preferences updated successfully.'))
        return super().form_valid(form)
