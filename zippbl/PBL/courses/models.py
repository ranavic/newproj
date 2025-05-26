from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User

class Category(models.Model):
    """
    Course categories (e.g., Programming, Data Science, Business)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text='FontAwesome icon class')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Skill(models.Model):
    """
    Skills that can be learned through courses
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='skills')
    
    def __str__(self):
        return self.name

class Course(models.Model):
    """
    Main course model
    """
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructor_courses')
    overview = models.TextField()
    description = models.TextField()
    learning_objectives = models.TextField(help_text='Comma-separated list of learning objectives')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    skills = models.ManyToManyField(Skill, related_name='courses', blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    promotional_video = models.URLField(blank=True, null=True)
    duration_in_hours = models.PositiveIntegerField(default=0, help_text='Estimated duration in hours')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    enrolled_students = models.ManyToManyField(
        User, through='Enrollment', related_name='enrolled_courses', blank=True
    )
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='required_for')
    languages = models.CharField(max_length=100, default='English', help_text='Comma-separated list of languages')
    certificate_available = models.BooleanField(default=True)
    allow_reviews = models.BooleanField(default=True)
    tags = models.CharField(max_length=200, blank=True, help_text='Comma-separated list of tags')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('course_detail', args=[self.slug])
    
    @property
    def rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 0
    
    @property
    def total_enrolled(self):
        return self.enrolled_students.count()
    
    @property
    def total_modules(self):
        return self.modules.count()
    
    @property
    def total_resources(self):
        return ResourceContent.objects.filter(module__course=self).count()

class Module(models.Model):
    """
    Course modules/sections
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_free_preview = models.BooleanField(default=False, help_text='Available for preview without enrollment')
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Content(models.Model):
    """
    Abstract base class for all types of module content
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['order']

class TextContent(Content):
    """
    Text-based content (e.g., lessons, articles)
    """
    content = models.TextField()
    estimated_reading_time = models.PositiveIntegerField(default=5, help_text='Estimated reading time in minutes')
    
    def __str__(self):
        return f"Text: {self.title}"

class VideoContent(Content):
    """
    Video content
    """
    video_url = models.URLField()
    duration = models.PositiveIntegerField(help_text='Duration in seconds')
    transcript = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Video: {self.title}"

class ResourceContent(Content):
    """
    Downloadable resources (e.g., PDFs, code files)
    """
    file = models.FileField(upload_to='course_resources/')
    file_type = models.CharField(max_length=20)
    file_size = models.PositiveIntegerField(help_text='File size in KB')
    
    def __str__(self):
        return f"Resource: {self.title}"

class Assignment(Content):
    """
    Course assignments
    """
    ASSIGNMENT_TYPES = (
        ('individual', 'Individual'),
        ('group', 'Group'),
        ('peer_graded', 'Peer Graded'),
    )
    
    instructions = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    total_points = models.PositiveIntegerField(default=100)
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES, default='individual')
    attachment = models.FileField(upload_to='assignments/', null=True, blank=True)
    
    def __str__(self):
        return f"Assignment: {self.title}"

class Enrollment(models.Model):
    """
    Tracks student enrollment in courses
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('refunded', 'Refunded'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    completion_percentage = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_accessed = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True, help_text='Access expiry date if applicable')
    certificate_issued = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

class Progress(models.Model):
    """
    Tracks student progress through course content
    """
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=20)  # text, video, resource, assignment
    content_id = models.PositiveIntegerField()
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)
    time_spent = models.PositiveIntegerField(default=0, help_text='Time spent in seconds')
    
    class Meta:
        unique_together = ['enrollment', 'content_type', 'content_id']
    
    def __str__(self):
        return f"Progress for {self.enrollment.student.username} - {self.content_type} {self.content_id}"

class Review(models.Model):
    """
    Course reviews and ratings
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.student.username} for {self.course.title}: {self.rating} stars"
