from django.urls import path
from . import views

urlpatterns = [
    # Course listing and detail views - essential functionality
    path('', views.course_list, name='course_list'),
    path('category/<slug:category_slug>/', views.course_list, name='course_list_by_category'),
    path('<slug:course_slug>/', views.course_detail, name='course_detail'),
    
    # Course enrollment - core functionality
    path('<slug:course_slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
    
    # Reviews functionality
    path('<slug:course_slug>/reviews/', views.course_reviews, name='course_reviews'),
    path('<slug:course_slug>/reviews/add/', views.add_review, name='add_review'),
    
    # Single instructor dashboard view that's confirmed to work
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    
    # Course content views - will be implemented in full version
    # path('<slug:course_slug>/modules/', views.course_modules, name='course_modules'),
    # path('<slug:course_slug>/module/<int:module_id>/', views.module_detail, name='module_detail'),
]
