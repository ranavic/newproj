from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from courses.models import Course, Module

class Badge(models.Model):
    """
    Badges that users can earn through various achievements
    """
    BADGE_LEVELS = (
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    level = models.CharField(max_length=20, choices=BADGE_LEVELS, default='bronze')
    points_awarded = models.PositiveIntegerField(default=0)
    requirement_description = models.TextField(help_text='Description of how to earn this badge')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

class Achievement(models.Model):
    """
    Achievements that users can unlock
    """
    ACHIEVEMENT_TYPES = (
        ('course_completion', 'Course Completion'),
        ('streak', 'Learning Streak'),
        ('quiz_score', 'Quiz Score'),
        ('contribution', 'Community Contribution'),
        ('skill_mastery', 'Skill Mastery'),
        ('special', 'Special Achievement'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.ImageField(upload_to='achievements/')
    points_awarded = models.PositiveIntegerField(default=0)
    badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True, related_name='achievements')
    is_hidden = models.BooleanField(default=False, help_text='Hidden achievements are not visible until unlocked')
    required_value = models.PositiveIntegerField(default=1, help_text='Required value to unlock (e.g., days for streaks)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    """
    Tracks achievements earned by users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='users_earned')
    date_earned = models.DateTimeField(auto_now_add=True)
    value_achieved = models.PositiveIntegerField(default=1, help_text='Value achieved to earn this (e.g., streak days)')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_achievements')
    is_showcased = models.BooleanField(default=False, help_text='Displayed on user profile')
    
    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-date_earned']
    
    def __str__(self):
        return f"{self.user.username} earned {self.achievement.name}"

class Level(models.Model):
    """
    User experience levels configuration
    """
    level_number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    min_points = models.PositiveIntegerField()
    max_points = models.PositiveIntegerField()
    icon = models.ImageField(upload_to='levels/', blank=True, null=True)
    perks_description = models.TextField(blank=True, help_text='Description of perks for this level')
    
    class Meta:
        ordering = ['level_number']
    
    def __str__(self):
        return f"Level {self.level_number}: {self.name or 'Unnamed'}"

class PointTransaction(models.Model):
    """
    Tracks point transactions for users
    """
    TRANSACTION_TYPES = (
        ('course_progress', 'Course Progress'),
        ('quiz_completion', 'Quiz Completion'),
        ('streak_bonus', 'Streak Bonus'),
        ('achievement_earned', 'Achievement Earned'),
        ('community_contribution', 'Community Contribution'),
        ('referral_bonus', 'Referral Bonus'),
        ('admin_adjustment', 'Administrative Adjustment'),
        ('challenge_completion', 'Challenge Completion'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    points = models.IntegerField(help_text='Can be positive or negative')
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    related_object_type = models.CharField(max_length=50, blank=True, null=True, help_text='Type of related object (e.g., course, quiz)')
    related_object_id = models.PositiveIntegerField(blank=True, null=True, help_text='ID of the related object')
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='awarded_points')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.points} points ({self.transaction_type})"

class Streak(models.Model):
    """
    Tracks user learning streaks
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak_days = models.PositiveIntegerField(default=0)
    longest_streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(default=timezone.now)
    streak_freeze_count = models.PositiveIntegerField(default=0, help_text='Number of streak freezes available')
    total_activity_days = models.PositiveIntegerField(default=0, help_text='Total days with learning activity')
    
    def __str__(self):
        return f"{self.user.username}'s Streak: {self.current_streak_days} days"
    
    def update_streak(self, activity_date=None):
        """Update user streak based on activity"""
        today = timezone.now().date() if activity_date is None else activity_date
        last_date = self.last_activity_date
        
        # Same day, nothing to update
        if today == last_date:
            return False
            
        # Activity on next day, continue streak
        if (today - last_date).days == 1:
            self.current_streak_days += 1
            self.last_activity_date = today
            self.total_activity_days += 1
            
            # Update longest streak if needed
            if self.current_streak_days > self.longest_streak_days:
                self.longest_streak_days = self.current_streak_days
                
            self.save()
            return True
            
        # Missed a day, check for streak freeze
        elif (today - last_date).days == 2 and self.streak_freeze_count > 0:
            self.streak_freeze_count -= 1
            self.last_activity_date = today
            self.total_activity_days += 1
            self.save()
            return True
            
        # Streak broken, reset
        elif (today - last_date).days > 1:
            self.current_streak_days = 1
            self.last_activity_date = today
            self.total_activity_days += 1
            self.save()
            return False
            
        return False

class Challenge(models.Model):
    """
    Time-limited challenges for users to complete
    """
    CHALLENGE_TYPES = (
        ('course_completion', 'Complete Course'),
        ('quiz_mastery', 'Quiz Mastery'),
        ('streak', 'Maintain Streak'),
        ('engagement', 'Engagement Challenge'),
        ('skill_acquisition', 'Skill Acquisition'),
        ('contribution', 'Community Contribution'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=30, choices=CHALLENGE_TYPES)
    points_reward = models.PositiveIntegerField(default=0)
    badge_reward = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    target_value = models.PositiveIntegerField(default=1, help_text='Target value to complete the challenge')
    courses = models.ManyToManyField(Course, blank=True, related_name='challenges')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

class UserChallenge(models.Model):
    """
    Tracks user progress on challenges
    """
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('abandoned', 'Abandoned'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    current_value = models.PositiveIntegerField(default=0, help_text='Current progress value')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reward_claimed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.username}'s progress on {self.challenge.title}: {self.current_value}/{self.challenge.target_value}"
    
    @property
    def progress_percentage(self):
        return min(100, int((self.current_value / self.challenge.target_value) * 100))
