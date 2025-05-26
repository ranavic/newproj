"""
Temporary URL configuration for SkillForge project demo.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Simplified URL patterns for demo
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Home page and static pages
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    
    # Course pages
    path('courses/', TemplateView.as_view(template_name='courses/course_list.html'), name='course_list'),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
