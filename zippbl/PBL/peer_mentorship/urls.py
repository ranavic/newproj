from django.urls import path
from . import views

urlpatterns = [
    # Mentor and mentee profiles
    path('', views.mentorship_home, name='mentorship_home'),
    path('become-mentor/', views.become_mentor, name='become_mentor'),
    path('mentor-profile/<int:user_id>/', views.mentor_profile, name='mentor_profile'),
    path('mentor-profile/edit/', views.edit_mentor_profile, name='edit_mentor_profile'),
    path('mentee-profile/edit/', views.edit_mentee_profile, name='edit_mentee_profile'),
    
    # Mentor discovery
    path('find-mentors/', views.find_mentors, name='find_mentors'),
    path('find-mentors/<slug:skill_slug>/', views.find_mentors_by_skill, name='find_mentors_by_skill'),
    path('find-mentors/<slug:course_slug>/', views.find_mentors_by_course, name='find_mentors_by_course'),
    
    # Mentorship relationships
    path('request/<int:mentor_id>/', views.request_mentorship, name='request_mentorship'),
    path('requests/', views.mentorship_requests, name='mentorship_requests'),
    path('requests/<int:relationship_id>/accept/', views.accept_mentorship, name='accept_mentorship'),
    path('requests/<int:relationship_id>/reject/', views.reject_mentorship, name='reject_mentorship'),
    path('mentorships/', views.my_mentorships, name='my_mentorships'),
    path('mentorships/<int:relationship_id>/', views.mentorship_detail, name='mentorship_detail'),
    path('mentorships/<int:relationship_id>/complete/', views.complete_mentorship, name='complete_mentorship'),
    
    # Mentorship sessions
    path('mentorships/<int:relationship_id>/sessions/', views.mentorship_sessions, name='mentorship_sessions'),
    path('mentorships/<int:relationship_id>/sessions/schedule/', views.schedule_session, name='schedule_session'),
    path('sessions/<int:session_id>/', views.session_detail, name='mentorship_session_detail'),
    path('sessions/<int:session_id>/start/', views.start_session, name='start_mentorship_session'),
    path('sessions/<int:session_id>/complete/', views.complete_session, name='complete_mentorship_session'),
    path('sessions/<int:session_id>/cancel/', views.cancel_session, name='cancel_mentorship_session'),
    
    # Reviews
    path('mentorships/<int:relationship_id>/review-mentor/', views.review_mentor, name='review_mentor'),
    path('mentorships/<int:relationship_id>/review-mentee/', views.review_mentee, name='review_mentee'),
    path('mentor-reviews/<int:user_id>/', views.mentor_reviews, name='mentor_reviews'),
    
    # Resources
    path('resources/', views.mentorship_resources, name='mentorship_resources'),
    path('resources/create/', views.create_resource, name='create_mentorship_resource'),
    path('resources/<int:resource_id>/', views.resource_detail, name='mentorship_resource_detail'),
]
