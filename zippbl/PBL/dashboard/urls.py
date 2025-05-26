from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard view
    path('', views.dashboard, name='dashboard'),
    
    # Simplified dashboard functionality
    path('widgets/', views.widgets, name='widgets'),
    path('goals/', views.study_goals, name='study_goals'),
    path('notes/', views.notes, name='notes'),
    path('tasks/', views.tasks, name='tasks'),
    path('reminders/', views.reminders, name='reminders'),
    
    # Announcements
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/<int:announcement_id>/acknowledge/', views.acknowledge_announcement, name='acknowledge_announcement'),
    
    # Calendar and schedule
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/events/', views.calendar_events, name='calendar_events'),
    
    # Analytics
    path('analytics/', views.user_analytics, name='analytics'),
    path('analytics/progress/', views.learning_progress, name='learning_progress'),
    path('analytics/activity/', views.activity_history, name='activity_history'),
]
