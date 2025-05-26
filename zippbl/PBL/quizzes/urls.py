from django.urls import path
from . import views

urlpatterns = [
    # Quiz listing and detail views
    path('', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    path('<int:quiz_id>/review/', views.quiz_review, name='quiz_review'),
    
    # Quiz history
    path('history/', views.quiz_history, name='quiz_history'),
    path('history/<int:attempt_id>/', views.attempt_detail, name='attempt_detail'),
    
    # Instructor views
    path('instructor/create/', views.create_quiz, name='create_quiz'),
    path('instructor/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('instructor/<int:quiz_id>/questions/', views.manage_questions, name='manage_questions'),
    path('instructor/<int:quiz_id>/questions/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('instructor/<int:quiz_id>/questions/add/', views.add_question, name='add_question'),
    path('instructor/<int:quiz_id>/questions/<int:question_id>/options/', views.manage_options, name='manage_options'),
    
    # AI-generated questions
    path('ai-questions/', views.ai_question_list, name='ai_question_list'),
    path('ai-questions/<int:question_id>/use/', views.use_ai_question, name='use_ai_question'),
]
