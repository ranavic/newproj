from django.urls import path
from . import views

urlpatterns = [
    # Achievements and badges
    path('', views.gamification_home, name='gamification_home'),
    path('achievements/', views.achievement_list, name='achievement_list'),
    path('achievements/<int:achievement_id>/', views.achievement_detail, name='achievement_detail'),
    path('badges/', views.badge_list, name='badge_list'),
    path('badges/<int:badge_id>/', views.badge_detail, name='badge_detail'),
    
    # Leaderboards
    path('leaderboards/', views.leaderboard_list, name='leaderboard_list'),
    path('leaderboards/global/', views.global_leaderboard, name='global_leaderboard'),
    path('leaderboards/course/<slug:course_slug>/', views.course_leaderboard, name='course_leaderboard'),
    path('leaderboards/skills/<slug:skill_slug>/', views.skill_leaderboard, name='skill_leaderboard'),
    
    # Points and leveling
    path('points/history/', views.points_history, name='points_history'),
    path('levels/', views.level_progression, name='level_progression'),
    
    # Streaks
    path('streaks/', views.streak_info, name='streak_info'),
    path('streaks/freeze/', views.add_streak_freeze, name='add_streak_freeze'),
    
    # Challenges
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/current/', views.current_challenges, name='current_challenges'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:challenge_id>/join/', views.join_challenge, name='join_challenge'),
    path('challenges/<int:challenge_id>/progress/', views.challenge_progress, name='challenge_progress'),
    
    # Admin views
    path('admin/achievements/', views.manage_achievements, name='manage_achievements'),
    path('admin/badges/', views.manage_badges, name='manage_badges'),
    path('admin/challenges/', views.manage_challenges, name='manage_challenges'),
]
