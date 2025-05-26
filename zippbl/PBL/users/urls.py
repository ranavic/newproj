from django.urls import path
from .views import (
    register, user_login, user_logout, profile,
    ProfileUpdateView, PreferenceUpdateView
)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/preferences/', PreferenceUpdateView.as_view(), name='preferences_update'),
]
