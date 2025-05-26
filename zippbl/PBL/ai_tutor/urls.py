from django.urls import path
from . import views

urlpatterns = [
    # AI Tutor sessions
    path('', views.ai_tutor_home, name='ai_tutor_home'),
    path('sessions/', views.session_list, name='ai_session_list'),
    path('sessions/new/', views.create_session, name='create_ai_session'),
    path('sessions/<int:session_id>/', views.session_detail, name='ai_session_detail'),
    path('sessions/<int:session_id>/chat/', views.session_chat, name='ai_session_chat'),
    path('sessions/<int:session_id>/end/', views.end_session, name='end_ai_session'),
    
    # API endpoint for sending/receiving messages
    path('api/send-message/<int:session_id>/', views.send_message, name='ai_send_message'),
    
    # Resources
    path('resources/', views.learning_resource_list, name='learning_resource_list'),
    path('resources/<int:resource_id>/', views.learning_resource_detail, name='learning_resource_detail'),
    
    # Concept explanations
    path('concepts/', views.concept_explanation_list, name='concept_list'),
    path('concepts/<int:concept_id>/', views.concept_explanation_detail, name='concept_detail'),
    path('concepts/search/', views.search_concepts, name='search_concepts'),
    
    # Feedback
    path('feedback/submit/<int:message_id>/', views.submit_feedback, name='submit_ai_feedback'),
    
    # Admin views
    path('admin/models/', views.ai_model_list, name='ai_model_list'),
    path('admin/models/<int:model_id>/edit/', views.edit_ai_model, name='edit_ai_model'),
    path('admin/prompt-templates/', views.prompt_template_list, name='prompt_template_list'),
    path('admin/prompt-templates/<int:template_id>/edit/', views.edit_prompt_template, name='edit_prompt_template'),
]
