from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from users.models import User
from courses.models import Course, Module

class Quiz(models.Model):
    """
    Quiz model linked to course modules
    """
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('expert', 'Expert'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    time_limit = models.PositiveIntegerField(help_text='Time limit in minutes', null=True, blank=True)
    total_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=40)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    allow_multiple_attempts = models.BooleanField(default=True)
    max_attempts = models.PositiveIntegerField(default=3, help_text='Maximum number of attempts allowed')
    randomize_questions = models.BooleanField(default=True)
    show_answers = models.BooleanField(default=False, help_text='Show correct answers after submission')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('quiz')
        verbose_name_plural = _('quizzes')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.course.title})"
    
    @property
    def total_questions(self):
        return self.questions.count()
    
    @property
    def total_marks_sum(self):
        return sum(question.marks for question in self.questions.all())

class Question(models.Model):
    """
    Quiz questions
    """
    QUESTION_TYPES = (
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('fill_blank', 'Fill in the Blank'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay/Long Answer'),
        ('matching', 'Matching'),
        ('code', 'Code Implementation'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    explanation = models.TextField(blank=True, help_text='Explanation of the correct answer')
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    image = models.ImageField(upload_to='quiz_questions/', blank=True, null=True)
    code_snippet = models.TextField(blank=True, help_text='Code snippet for code-related questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question_text[:50]}..."
    
    def clean(self):
        if self.question_type == 'true_false':
            # Ensure there are exactly 2 options for True/False questions
            if self.options.count() != 2:
                raise ValidationError({'question_type': _('True/False questions must have exactly 2 options.')})
            
            # Ensure one is marked as correct
            if self.options.filter(is_correct=True).count() != 1:
                raise ValidationError({'options': _('True/False questions must have exactly one correct option.')})
                
        elif self.question_type in ['single_choice', 'multiple_choice', 'matching']:
            # Ensure there are at least 2 options for choice questions
            if self.options.count() < 2:
                raise ValidationError({'question_type': _('Choice questions must have at least 2 options.')})
            
            # For single choice, ensure only one option is marked as correct
            if self.question_type == 'single_choice' and self.options.filter(is_correct=True).count() != 1:
                raise ValidationError({'options': _('Single choice questions must have exactly one correct option.')})
            
            # For multiple choice, ensure at least one option is marked as correct
            if self.question_type == 'multiple_choice' and self.options.filter(is_correct=True).count() < 1:
                raise ValidationError({'options': _('Multiple choice questions must have at least one correct option.')})

class QuestionOption(models.Model):
    """
    Options for quiz questions
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.option_text} ({'Correct' if self.is_correct else 'Incorrect'})"
    
    def clean(self):
        # Validate based on question type
        if self.question.question_type == 'true_false':
            if self.option_text.lower() not in ['true', 'false']:
                raise ValidationError({'option_text': _('Options for True/False questions must be either "True" or "False".')})

class QuizAttempt(models.Model):
    """
    Tracks student quiz attempts
    """
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('timed_out', 'Timed Out'),
        ('cancelled', 'Cancelled'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_taken = models.PositiveIntegerField(null=True, blank=True, help_text='Time taken in seconds')
    attempt_number = models.PositiveIntegerField(default=1)
    passed = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True, help_text='Instructor feedback')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        unique_together = ['quiz', 'student', 'attempt_number']
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.student.username}'s attempt #{self.attempt_number} on {self.quiz.title}"
    
    @property
    def is_latest_attempt(self):
        return self.attempt_number == QuizAttempt.objects.filter(
            quiz=self.quiz, student=self.student
        ).aggregate(models.Max('attempt_number'))['attempt_number__max']

class StudentAnswer(models.Model):
    """
    Student's answers to quiz questions
    """
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(QuestionOption, blank=True, related_name='student_selections')
    text_answer = models.TextField(blank=True, null=True, help_text='For fill in the blank, short answer, or essay questions')
    code_answer = models.TextField(blank=True, null=True, help_text='For code implementation questions')
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    feedback = models.TextField(blank=True, null=True, help_text='Automated or instructor feedback')
    submission_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['quiz_attempt', 'question']
    
    def __str__(self):
        return f"Answer by {self.quiz_attempt.student.username} for {self.question}"

class AIGeneratedQuestion(models.Model):
    """
    AI-generated questions that can be added to quizzes
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ai_questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=Question.QUESTION_TYPES)
    difficulty = models.CharField(max_length=10, choices=Quiz.DIFFICULTY_CHOICES, default='medium')
    explanation = models.TextField(blank=True)
    topic = models.CharField(max_length=100)
    marks = models.PositiveIntegerField(default=1)
    is_verified = models.BooleanField(default=False, help_text='Verified by an instructor')
    created_at = models.DateTimeField(auto_now_add=True)
    used_count = models.PositiveIntegerField(default=0, help_text='Number of times this question has been used')
    
    def __str__(self):
        return f"AI Question: {self.question_text[:50]}..."
