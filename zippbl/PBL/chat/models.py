from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from users.models import User
from courses.models import Course

class ChatRoom(models.Model):
    """
    Chat room for real-time messaging
    """
    ROOM_TYPES = (
        ('private', 'Private Chat'),
        ('group', 'Group Chat'),
        ('course', 'Course Discussion'),
        ('support', 'Support Chat'),
        ('live_class', 'Live Class Chat'),
    )
    
    name = models.CharField(max_length=255)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    participants = models.ManyToManyField(User, related_name='chat_rooms', through='ChatRoomMember')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='chat_rooms/', null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name

class ChatRoomMember(models.Model):
    """
    User membership in chat rooms with role information
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
        ('guest', 'Guest'),
    )
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    muted_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['chat_room', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.chat_room.name} as {self.get_role_display()}"
    
    @property
    def is_muted(self):
        if not self.muted_until:
            return False
        return self.muted_until > timezone.now()

class Message(models.Model):
    """
    Chat messages
    """
    MESSAGE_TYPES = (
        ('text', 'Text Message'),
        ('image', 'Image Message'),
        ('file', 'File Message'),
        ('audio', 'Audio Message'),
        ('video', 'Video Message'),
        ('system', 'System Message'),
        ('code', 'Code Snippet'),
    )
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    attachment_preview = models.ImageField(upload_to='chat_previews/', null=True, blank=True)
    attachment_name = models.CharField(max_length=100, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['sent_at']
    
    def __str__(self):
        return f"Message by {self.sender.username if self.sender else 'System'} in {self.chat_room.name}"
    
    def edit_message(self, new_content):
        self.content = new_content
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()

class MessageRead(models.Model):
    """
    Tracks when users read messages
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_messages')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.message} read by {self.user.username} at {self.read_at}"

class LiveSession(models.Model):
    """
    Live video and audio sessions
    """
    SESSION_TYPES = (
        ('one_on_one', 'One-on-One'),
        ('group', 'Group Call'),
        ('webinar', 'Webinar'),
        ('live_class', 'Live Class'),
    )
    
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    )
    
    title = models.CharField(max_length=200)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_sessions')
    participants = models.ManyToManyField(User, related_name='joined_sessions')
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='live_sessions')
    description = models.TextField(blank=True)
    session_url = models.URLField(blank=True, null=True)
    recording_url = models.URLField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(default=10)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scheduled_start']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def duration_minutes(self):
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return delta.total_seconds() // 60
        return None
    
    def start_session(self):
        self.status = 'in_progress'
        self.actual_start = timezone.now()
        self.save()
    
    def end_session(self):
        self.status = 'ended'
        self.actual_end = timezone.now()
        self.save()
