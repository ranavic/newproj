from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .auth_views import register_view
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import home,dashboard_view

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Home page - Using a view for home
    path('', home, name='home'),

    # Dashboard views (still using TemplateView for static templates)
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard/dashboard.html'), name='dashboard'),
    path('dashboard/widgets/', TemplateView.as_view(template_name='dashboard/widgets.html'), name='widgets'),
    path('dashboard/goals/', TemplateView.as_view(template_name='dashboard/study_goals.html'), name='study_goals'),
    path('dashboard/notes/', TemplateView.as_view(template_name='dashboard/notes.html'), name='notes'),
    path('dashboard/announcements/', TemplateView.as_view(template_name='dashboard/announcements.html'), name='announcements'),

    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/register/', register_view, name='register'),

    # Password reset URLs
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Course URLs (using TemplateView for static content)
    path('courses/', TemplateView.as_view(template_name='placeholder.html'), name='course_list'),
    path('courses/<slug:course_slug>/', TemplateView.as_view(template_name='courses/course_detail.html'), name='course_detail'),

    # Additional feature placeholders
    path('quizzes/', TemplateView.as_view(template_name='placeholder.html'), name='quizzes'),
    path('ai-tutor/', TemplateView.as_view(template_name='placeholder.html'), name='ai_tutor'),
    path('mentorship/', TemplateView.as_view(template_name='placeholder.html'), name='mentorship'),
    path('certificates/', TemplateView.as_view(template_name='placeholder.html'), name='certificates'),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
