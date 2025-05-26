from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """Custom User model for SkillForge"""
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Administrator'),
    )
    
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default='en')
    
    # For Gamification
    experience_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak_days = models.IntegerField(default=0)
    last_activity_date = models.DateField(blank=True, null=True)
    
    # Social links
    linkedin_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_student(self):
        return self.user_type == 'student'
    
    @property
    def is_instructor(self):
        return self.user_type == 'instructor'
    
    @property
    def is_admin_user(self):
        return self.user_type == 'admin'

class UserPreference(models.Model):
    """Model to store user preferences for personalized learning"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    learning_pace = models.CharField(
        max_length=20, 
        choices=(
            ('slow', 'Slow'),
            ('medium', 'Medium'),
            ('fast', 'Fast'),
        ),
        default='medium'
    )
    preferred_content_type = models.CharField(
        max_length=20,
        choices=(
            ('video', 'Video'),
            ('text', 'Text'),
            ('interactive', 'Interactive'),
            ('mixed', 'Mixed'),
        ),
        default='mixed'
    )
    notification_preferences = models.JSONField(default=dict)
    study_reminder_time = models.TimeField(null=True, blank=True)
    
    # Learning style preferences (based on VARK model)
    visual_preference = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5,
        help_text='Preference for visual learning materials (1-10)'
    )
    auditory_preference = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5,
        help_text='Preference for auditory learning materials (1-10)'
    )
    reading_preference = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5,
        help_text='Preference for reading/writing learning materials (1-10)'
    )
    kinesthetic_preference = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5,
        help_text='Preference for hands-on learning materials (1-10)'
    )
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
