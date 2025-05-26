"""
Minimal URL configuration for SkillForge project.
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .auth_views import register_view

from django.shortcuts import render

# Use our proper home template instead of hardcoded HTML
def home_view(request):
    return render(request, 'home.html')

# URL patterns for the SkillForge platform
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Use our properly styled home template
    path('', home_view, name='home'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='minimal_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', register_view, name='register'),
    
    # Course pages
    path('courses/', TemplateView.as_view(template_name='courses/course_list.html'), name='course_list'),
    path('courses/<slug:course_slug>/', TemplateView.as_view(template_name='placeholder.html'), name='course_detail'),
    
    # Dashboard page
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    
    # AI Tutor page
    path('ai-tutor/', TemplateView.as_view(template_name='ai_tutor.html'), name='ai_tutor'),
    
    # Mentorship page
    path('mentorship/', TemplateView.as_view(template_name='mentorship.html'), name='mentorship'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
