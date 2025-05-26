from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.http import JsonResponse

from courses.models import Course, Enrollment
from users.models import User

@login_required
def dashboard(request):
    """
    Main dashboard view showing user's learning progress and recommendations
    """
    user = request.user
    
    # Get user's enrollments
    enrollments = Enrollment.objects.filter(student=user)
    enrolled_count = enrollments.count()
    completed_count = enrollments.filter(status='completed').count()
    
    # Get in-progress courses
    in_progress_courses = enrollments.filter(
        status='active'
    ).order_by('-last_accessed')[:3]
    
    # Get recommended courses based on user's interests and previous enrollments
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    
    # Try to get recommendations based on user preferences
    try:
        user_preferences = user.preferences
        # Get courses that match user's preferences but user is not enrolled in
        recommended_courses = Course.objects.filter(
            status='published'
        ).exclude(
            id__in=enrolled_course_ids
        )
        
        # If the user has learning preferences, filter by those
        if hasattr(user_preferences, 'preferred_content_type') and user_preferences.preferred_content_type != 'mixed':
            # This is a simplified recommendation logic
            if user_preferences.preferred_content_type == 'video':
                recommended_courses = recommended_courses.filter(video_content_count__gt=0)
            elif user_preferences.preferred_content_type == 'text':
                recommended_courses = recommended_courses.filter(text_content_count__gt=0)
                
    except Exception as e:
        # If user has no preferences or an error occurs, show popular courses
        recommended_courses = Course.objects.filter(status='published').exclude(
            id__in=enrolled_course_ids
        ).annotate(
            student_count=Count('enrolled_students')
        ).order_by('-student_count')
    
    # Annotate with average rating
    recommended_courses = recommended_courses.annotate(
        avg_rating=Avg('reviews__rating')
    )[:3]
    
    # Get certificate count (simplified for now)
    certificate_count = 0  # This would pull from certificates app in full implementation
    
    # If user accessed dashboard, update streak
    last_activity = user.last_activity_date
    today = timezone.now().date()
    
    if last_activity is None or last_activity != today:
        # Update user's last activity and potentially streak
        user.last_activity_date = today
        
        # If the last activity was yesterday, increment streak
        if last_activity is not None and (today - last_activity).days == 1:
            user.streak_days += 1
        # If more than one day has passed, reset streak
        elif last_activity is not None and (today - last_activity).days > 1:
            user.streak_days = 1
        # If this is the first activity ever, start streak at 1
        elif last_activity is None:
            user.streak_days = 1
            
        user.save()
    
    context = {
        'enrolled_count': enrolled_count,
        'completed_count': completed_count,
        'certificate_count': certificate_count,
        'in_progress_courses': in_progress_courses,
        'recommended_courses': recommended_courses,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def widgets(request):
    """
    Manage dashboard widgets and their layout
    """
    # In a full implementation, this would allow users to customize their dashboard
    return render(request, 'dashboard/widgets.html')

@login_required
def study_goals(request):
    """
    Manage user's study goals
    """
    # In a full implementation, this would allow users to set and track learning goals
    return render(request, 'dashboard/study_goals.html')

@login_required
def notes(request):
    """
    View and manage user's learning notes
    """
    return render(request, 'dashboard/notes.html')

@login_required
def tasks(request):
    """
    View and manage user's learning tasks
    """
    return render(request, 'dashboard/tasks.html')

@login_required
def reminders(request):
    """
    View and manage user's learning reminders
    """
    return render(request, 'dashboard/reminders.html')

@login_required
def announcement_list(request):
    """
    View list of announcements
    """
    return render(request, 'dashboard/announcements.html')

@login_required
def announcement_detail(request, announcement_id):
    """
    View detail of a specific announcement
    """
    return render(request, 'dashboard/announcement_detail.html')

@login_required
def acknowledge_announcement(request, announcement_id):
    """
    Mark an announcement as acknowledged
    """
    # Placeholder function
    return redirect('announcement_list')

@login_required
def calendar_view(request):
    """
    View user's learning calendar
    """
    return render(request, 'dashboard/calendar.html')

@login_required
def calendar_events(request):
    """
    Get calendar events in JSON format
    """
    # Placeholder function that would return JSON in full implementation
    return JsonResponse({'events': []})

@login_required
def user_analytics(request):
    """
    View user's learning analytics dashboard
    """
    return render(request, 'dashboard/analytics.html')

@login_required
def learning_progress(request):
    """
    View detailed learning progress
    """
    return render(request, 'dashboard/learning_progress.html')

@login_required
def activity_history(request):
    """
    View learning activity history
    """
    return render(request, 'dashboard/activity_history.html')
