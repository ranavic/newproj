from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserPreference

class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    can_delete = False
    verbose_name_plural = 'Preferences'

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture', 
                                          'date_of_birth', 'phone_number', 'address')}),
        (_('User type'), {'fields': ('user_type',)}),
        (_('Preferences'), {'fields': ('preferred_language',)}),
        (_('Gamification'), {'fields': ('experience_points', 'level', 'streak_days', 'last_activity_date')}),
        (_('Social profiles'), {'fields': ('linkedin_profile', 'github_profile', 'website')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'level')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    inlines = (UserPreferenceInline,)

admin.site.register(User, UserAdmin)
