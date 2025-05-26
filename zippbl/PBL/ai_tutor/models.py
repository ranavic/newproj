from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from users.models import User
from courses.models import Course, Module

class AIModel(models.Model):
    """
    AI Model configurations for the AI Tutor
    """
    MODEL_TYPES = (
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ('gpt-4', 'GPT-4'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('custom', 'Custom Model'),
    )
    
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    api_key_variable = models.CharField(max_length=100, help_text='Environment variable name that stores the API key')
    endpoint = models.URLField(blank=True, null=True)
    max_tokens = models.PositiveIntegerField(default=1000)
    temperature = models.FloatField(default=0.7)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one default model
        if self.is_default:
            AIModel.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class AITutorSession(models.Model):
    """
    AI Tutor session for a user
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_tutor_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ai_tutor_sessions', null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='ai_tutor_sessions', null=True, blank=True)
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    session_name = models.CharField(max_length=200, default='New AI Tutor Session')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)
    token_usage = models.PositiveIntegerField(default=0)
    session_context = models.JSONField(default=dict, help_text='Stores session context and metadata')
    system_prompt = models.TextField(blank=True, help_text='Custom system prompt for this session')
    
    class Meta:
        ordering = ['-last_interaction']
    
    def __str__(self):
        return f"{self.user.username}'s AI Tutor Session - {self.session_name}"
    
    @property
    def is_expired(self):
        # Session expires after 3 days of inactivity
        return (timezone.now() - self.last_interaction).days > 3
    
    @property
    def message_count(self):
        return self.messages.count()
    
    def end_session(self):
        self.status = 'completed'
        self.save()

class AITutorMessage(models.Model):
    """
    Messages exchanged in an AI Tutor session
    """
    MESSAGE_TYPES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    
    session = models.ForeignKey(AITutorSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tokens = models.PositiveIntegerField(default=0, help_text='Token count of this message')
    metadata = models.JSONField(default=dict, blank=True, help_text='Additional metadata for the message')
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_message_type_display()} Message ({self.session})"

class LearningResource(models.Model):
    """
    AI-recommended learning resources
    """
    RESOURCE_TYPES = (
        ('article', 'Article'),
        ('video', 'Video'),
        ('book', 'Book'),
        ('course', 'Course'),
        ('tutorial', 'Tutorial'),
        ('documentation', 'Documentation'),
        ('exercise', 'Exercise'),
        ('tool', 'Tool'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    difficulty_level = models.CharField(
        max_length=20,
        choices=(
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ),
        default='intermediate'
    )
    tags = models.CharField(max_length=200, blank=True, help_text='Comma-separated tags')
    created_at = models.DateTimeField(auto_now_add=True)
    ai_generated = models.BooleanField(default=True)
    verified = models.BooleanField(default=False, help_text='Verified by an instructor')
    
    def __str__(self):
        return self.title

class AITutorFeedback(models.Model):
    """
    User feedback on AI Tutor responses
    """
    message = models.ForeignKey(AITutorMessage, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"Feedback by {self.user.username} on message {self.message.id}: {self.rating}/5"

class AITutorPromptTemplate(models.Model):
    """
    Predefined prompt templates for the AI Tutor
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    prompt_template = models.TextField(help_text='Prompt template with placeholders like {course}, {concept}, etc.')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_prompt_templates')
    is_global = models.BooleanField(default=False, help_text='If true, available for all courses')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ConceptExplanation(models.Model):
    """
    AI-generated concept explanations stored for reuse
    """
    concept = models.CharField(max_length=200)
    explanation = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='concept_explanations')
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True, related_name='concept_explanations')
    generated_by = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, related_name='generated_explanations')
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_explanations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['concept', 'course']
    
    def __str__(self):
        return f"Explanation of '{self.concept}' for {self.course.title}"
