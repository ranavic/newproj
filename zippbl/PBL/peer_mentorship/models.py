from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from courses.models import Course, Skill

class MentorProfile(models.Model):
    """
    Extended profile for users who want to be mentors
    """
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paused', 'Paused'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    bio = models.TextField(help_text='Detailed mentor bio')
    expertise = models.ManyToManyField(Skill, related_name='expert_mentors')
    courses = models.ManyToManyField(Course, related_name='mentors', blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_accepting_mentees = models.BooleanField(default=True)
    max_mentees = models.PositiveIntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_skills = models.ManyToManyField(Skill, related_name='verified_mentors', blank=True)
    testimonial = models.TextField(blank=True)
    expert_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
        help_text='Expertise level from 1-5'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Mentor Profile"
    
    @property
    def current_mentee_count(self):
        return MentorshipRelationship.objects.filter(
            mentor=self.user,
            status='active'
        ).count()
    
    @property
    def is_available(self):
        return (self.is_accepting_mentees and 
                self.status == 'approved' and 
                self.current_mentee_count < self.max_mentees)

class MenteeProfile(models.Model):
    """
    Extended profile for users seeking mentorship
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentee_profile')
    learning_goals = models.TextField()
    skills_to_learn = models.ManyToManyField(Skill, related_name='interested_mentees', blank=True)
    preferred_mentorship_duration = models.CharField(
        max_length=50,
        choices=(
            ('short_term', 'Short Term (1-3 months)'),
            ('medium_term', 'Medium Term (3-6 months)'),
            ('long_term', 'Long Term (6+ months)'),
            ('project_based', 'Project Based'),
        ),
        default='medium_term'
    )
    availability = models.TextField(help_text='Describe your availability for mentorship sessions')
    current_experience_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1,
        help_text='Current expertise level from 1-5'
    )
    preferred_communication_style = models.CharField(
        max_length=50,
        choices=(
            ('structured', 'Structured and Scheduled'),
            ('flexible', 'Flexible and Casual'),
            ('mixed', 'Mixed Approach'),
        ),
        default='mixed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Mentee Profile"

class MentorshipRelationship(models.Model):
    """
    Tracks the relationship between mentors and mentees
    """
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorships_given')
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorships_received')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentorships')
    skills = models.ManyToManyField(Skill, related_name='mentorships', blank=True)
    goals = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    expected_duration = models.PositiveIntegerField(help_text='Expected duration in weeks', default=12)
    meeting_frequency = models.CharField(
        max_length=50,
        choices=(
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
            ('custom', 'Custom'),
        ),
        default='weekly'
    )
    custom_meeting_schedule = models.TextField(blank=True, help_text='If custom frequency is selected')
    mentor_feedback = models.TextField(blank=True, help_text='Mentor\'s feedback about the mentee')
    mentee_feedback = models.TextField(blank=True, help_text='Mentee\'s feedback about the mentor')
    
    class Meta:
        unique_together = ['mentor', 'mentee', 'course']
    
    def __str__(self):
        return f"{self.mentor.username} mentoring {self.mentee.username} ({self.get_status_display()})"
    
    def accept(self):
        self.status = 'accepted'
        self.save()
    
    def activate(self):
        self.status = 'active'
        self.started_at = timezone.now()
        self.save()
    
    def complete(self):
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save()

class MentorshipSession(models.Model):
    """
    Individual mentorship sessions
    """
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('no_show', 'No Show'),
    )
    
    mentorship = models.ForeignKey(MentorshipRelationship, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    meeting_url = models.URLField(blank=True, null=True, help_text='Video meeting URL')
    meeting_notes = models.TextField(blank=True)
    learning_objectives = models.TextField(blank=True, help_text='Objectives for this session')
    outcomes = models.TextField(blank=True, help_text='Outcomes and accomplishments')
    follow_up_actions = models.TextField(blank=True, help_text='Follow-up actions for mentee')
    resources_shared = models.TextField(blank=True, help_text='Resources shared during the session')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scheduled_start']
    
    def __str__(self):
        return f"Session: {self.title} ({self.mentorship})"
    
    def start_session(self):
        self.status = 'in_progress'
        self.actual_start = timezone.now()
        self.save()
    
    def complete_session(self):
        self.status = 'completed'
        self.actual_end = timezone.now()
        self.save()

class MentorReview(models.Model):
    """
    Reviews for mentors
    """
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_reviews')
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_mentor_reviews')
    mentorship = models.ForeignKey(MentorshipRelationship, on_delete=models.CASCADE, related_name='mentor_reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    knowledge_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    availability_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    helpfulness_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_recommended = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['mentee', 'mentorship']
    
    def __str__(self):
        return f"Review of {self.mentor.username} by {self.mentee.username}: {self.rating}/5"
    
    @property
    def average_rating(self):
        ratings = [self.rating, self.knowledge_rating, self.communication_rating, 
                 self.availability_rating, self.helpfulness_rating]
        return sum(ratings) / len(ratings)

class MenteeReview(models.Model):
    """
    Reviews for mentees
    """
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentee_reviews')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_mentee_reviews')
    mentorship = models.ForeignKey(MentorshipRelationship, on_delete=models.CASCADE, related_name='mentee_reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    preparation_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    engagement_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    progress_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['mentor', 'mentorship']
    
    def __str__(self):
        return f"Review of {self.mentee.username} by {self.mentor.username}: {self.rating}/5"

class MentorshipResource(models.Model):
    """
    Resources shared between mentors and mentees
    """
    RESOURCE_TYPES = (
        ('document', 'Document'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('book', 'Book'),
        ('code', 'Code Sample'),
        ('tool', 'Tool'),
        ('exercise', 'Exercise'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='mentorship_resources/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_resources')
    mentorship = models.ForeignKey(MentorshipRelationship, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    session = models.ForeignKey(MentorshipSession, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    is_public = models.BooleanField(default=False, help_text='If public, can be shared with all users')
    skills = models.ManyToManyField(Skill, related_name='mentorship_resources', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
