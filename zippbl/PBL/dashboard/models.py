from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from users.models import User
from courses.models import Course

class UserDashboardPreference(models.Model):
    """
    User preferences for dashboard customization
    """
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System Default'),
        ('custom', 'Custom'),
    )
    
    LAYOUT_CHOICES = (
        ('grid', 'Grid'),
        ('list', 'List'),
        ('compact', 'Compact'),
        ('detailed', 'Detailed'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_preferences')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='system')
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='grid')
    show_streak = models.BooleanField(default=True)
    show_achievements = models.BooleanField(default=True)
    show_recommendations = models.BooleanField(default=True)
    show_calendar = models.BooleanField(default=True)
    show_upcoming_deadlines = models.BooleanField(default=True)
    enable_notifications = models.BooleanField(default=True)
    widgets_order = models.JSONField(default=list, blank=True, help_text='Ordered list of widget IDs')
    hidden_widgets = models.JSONField(default=list, blank=True, help_text='List of hidden widget IDs')
    custom_color_scheme = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Dashboard Preferences"

class WidgetType(models.Model):
    """
    Types of widgets available for the dashboard
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, help_text='Internal code for the widget')
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text='FontAwesome icon class')
    default_width = models.PositiveIntegerField(default=1, help_text='Default width in grid units')
    default_height = models.PositiveIntegerField(default=1, help_text='Default height in grid units')
    available_for_students = models.BooleanField(default=True)
    available_for_instructors = models.BooleanField(default=True)
    available_for_admins = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    requires_subscription = models.BooleanField(default=False)
    data_source = models.CharField(max_length=100, blank=True, null=True, help_text='API endpoint or data source')
    template_name = models.CharField(max_length=100, help_text='Template file for rendering')
    javascript_module = models.CharField(max_length=100, blank=True, null=True, help_text='JS module for dynamic functionality')
    settings_schema = models.JSONField(default=dict, blank=True, help_text='JSON schema for widget settings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class UserWidget(models.Model):
    """
    Instances of widgets configured by users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.ForeignKey(WidgetType, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True, null=True, help_text='Custom title (optional)')
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=1)
    height = models.PositiveIntegerField(default=1)
    settings = models.JSONField(default=dict, blank=True, help_text='User-specific widget settings')
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        custom_title = self.title if self.title else self.widget_type.name
        return f"{custom_title} ({self.user.username})"

class StudyGoal(models.Model):
    """
    User-defined study goals
    """
    PERIOD_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('abandoned', 'Abandoned'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    target_value = models.PositiveIntegerField(help_text='Target value (e.g., minutes of study time)')
    current_value = models.PositiveIntegerField(default=0)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='weekly')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False, help_text='Featured on dashboard')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    @property
    def progress_percentage(self):
        if self.target_value == 0:  # Avoid division by zero
            return 0
        return min(100, int((self.current_value / self.target_value) * 100))
    
    @property
    def is_achieved(self):
        return self.current_value >= self.target_value

class StudySession(models.Model):
    """
    Records of user study sessions
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    topics_covered = models.TextField(blank=True, help_text='Comma-separated list of topics')
    productivity_rating = models.PositiveIntegerField(null=True, blank=True, help_text='User self-rating (1-10)')
    notes = models.TextField(blank=True)
    offline_record = models.BooleanField(default=False, help_text='Session recorded while offline')
    last_synced = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Study session by {self.user.username} on {self.start_time.date()}"
    
    def complete_session(self, end_time=None):
        """Complete a study session and calculate duration"""
        self.end_time = end_time or timezone.now()
        self.is_completed = True
        
        # Calculate duration in minutes
        if self.start_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
        
        self.save()
        return self.duration_minutes

class Announcement(models.Model):
    """
    Platform-wide or course-specific announcements
    """
    ANNOUNCEMENT_TYPES = (
        ('platform', 'Platform-wide'),
        ('course', 'Course-specific'),
        ('user', 'User-specific'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_announcements')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
    target_users = models.ManyToManyField(User, blank=True, related_name='targeted_announcements')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    requires_acknowledgment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_current(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.end_date and now > self.end_date:
            return False
        return now >= self.start_date

class UserAnnouncementStatus(models.Model):
    """
    Tracks user interaction with announcements
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcement_statuses')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='user_statuses')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    hidden = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'announcement']
    
    def __str__(self):
        status = 'Read' if self.is_read else 'Unread'
        if self.acknowledged:
            status += ', Acknowledged'
        return f"{self.announcement.title}: {status} ({self.user.username})"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def acknowledge(self):
        self.acknowledged = True
        self.acknowledged_at = timezone.now()
        self.is_read = True
        self.read_at = self.read_at or timezone.now()
        self.save()
