from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import (
    Course, Category, Module, TextContent, VideoContent, 
    ResourceContent, Assignment, Enrollment, Progress, Review
)
from users.models import User

# Course listing views
def course_list(request, category_slug=None):
    """
    Display a list of available courses, with optional category filtering
    """
    categories = Category.objects.all()
    courses = Course.objects.filter(status='published')
    
    # Filter by category if provided
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        courses = courses.filter(category=category)
    
    # Filter by search query
    search_query = request.GET.get('q', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(overview__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filter by level
    level = request.GET.get('level', '')
    if level and level != 'all':
        courses = courses.filter(level=level)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'newest':
        courses = courses.order_by('-created_at')
    elif sort_by == 'rating':
        courses = courses.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    elif sort_by == 'popular':
        courses = courses.annotate(student_count=Count('enrolled_students')).order_by('-student_count')
    elif sort_by == 'price_low':
        courses = courses.order_by('price')
    elif sort_by == 'price_high':
        courses = courses.order_by('-price')
    
    # Pagination
    paginator = Paginator(courses, 9)  # 9 courses per page
    page = request.GET.get('page')
    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)
    
    context = {
        'categories': categories,
        'category': category,
        'courses': courses,
        'search_query': search_query,
        'level': level,
        'sort_by': sort_by,
        'level_choices': Course.LEVEL_CHOICES,
    }
    
    return render(request, 'courses/course_list.html', context)

def course_detail(request, course_slug):
    """
    Display detailed information about a course
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    modules = course.modules.all().order_by('order')
    
    # Get related courses
    related_courses = Course.objects.filter(
        Q(category=course.category) | Q(skills__in=course.skills.all())
    ).exclude(id=course.id).distinct()[:3]
    
    # Check if user is enrolled
    is_enrolled = False
    user_progress = 0
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, 
            course=course, 
            status__in=['active', 'completed']
        ).exists()
        
        if is_enrolled:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
            user_progress = enrollment.completion_percentage
    
    # Get reviews
    reviews = course.reviews.all().order_by('-created_at')[:5]
    review_count = course.reviews.count()
    
    # Check if user can review (must be enrolled and not already reviewed)
    can_review = False
    if request.user.is_authenticated and is_enrolled:
        can_review = not Review.objects.filter(course=course, student=request.user).exists()
    
    context = {
        'course': course,
        'modules': modules,
        'related_courses': related_courses,
        'is_enrolled': is_enrolled,
        'user_progress': user_progress,
        'reviews': reviews,
        'review_count': review_count,
        'can_review': can_review,
    }
    
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_slug):
    """
    Enroll a student in a course
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, _('You are already enrolled in this course.'))
        return redirect('course_detail', course_slug=course.slug)
    
    # If course is paid, redirect to payment (to be implemented)
    if course.price > 0:
        # In a real app, we would redirect to a payment flow here
        # For now, we'll just enroll the user directly
        pass
    
    # Create enrollment
    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course,
        status='active',
    )
    
    messages.success(request, _('Successfully enrolled in %s!') % course.title)
    return redirect('module_detail', course_slug=course.slug, module_id=course.modules.first().id)

@login_required
def my_courses(request):
    """
    Show courses that the user is enrolled in
    """
    enrollments = Enrollment.objects.filter(student=request.user).order_by('-date_enrolled')
    
    # Filter by status
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        enrollments = enrollments.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        enrollments = enrollments.filter(course__title__icontains=search_query)
    
    context = {
        'enrollments': enrollments,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'courses/my_courses.html', context)

@login_required
def course_modules(request, course_slug):
    """
    Show all modules for a course
    """
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is enrolled
    try:
        enrollment = Enrollment.objects.get(student=request.user, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, _('You need to enroll in this course to access its content.'))
        return redirect('course_detail', course_slug=course.slug)
    
    modules = course.modules.all().order_by('order')
    
    # Calculate progress for each module
    module_progress = {}
    for module in modules:
        total_contents = module.contents.count()
        if total_contents > 0:
            completed_contents = Progress.objects.filter(
                enrollment=enrollment,
                module=module,
                completed=True
            ).count()
            progress_percent = int((completed_contents / total_contents) * 100)
        else:
            progress_percent = 0
        
        module_progress[module.id] = progress_percent
    
    context = {
        'course': course,
        'modules': modules,
        'enrollment': enrollment,
        'module_progress': module_progress,
    }
    
    return render(request, 'courses/course_modules.html', context)

@login_required
def module_detail(request, course_slug, module_id):
    """
    Show a specific module and its contents
    """
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if module is free preview or if user is enrolled
    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course, status__in=['active', 'completed']
    ).exists()
    
    if not (module.is_free_preview or is_enrolled):
        messages.error(request, _('You need to enroll in this course to access this module.'))
        return redirect('course_detail', course_slug=course.slug)
    
    # Get module contents in order
    text_contents = TextContent.objects.filter(module=module).order_by('order')
    video_contents = VideoContent.objects.filter(module=module).order_by('order')
    resource_contents = ResourceContent.objects.filter(module=module).order_by('order')
    assignments = Assignment.objects.filter(module=module).order_by('order')
    
    # Combine and sort all contents
    all_contents = []
    for content in text_contents:
        all_contents.append({
            'id': content.id,
            'title': content.title,
            'order': content.order,
            'type': 'text',
            'content': content,
        })
    
    for content in video_contents:
        all_contents.append({
            'id': content.id,
            'title': content.title,
            'order': content.order,
            'type': 'video',
            'content': content,
        })
    
    for content in resource_contents:
        all_contents.append({
            'id': content.id,
            'title': content.title,
            'order': content.order,
            'type': 'resource',
            'content': content,
        })
    
    for content in assignments:
        all_contents.append({
            'id': content.id,
            'title': content.title,
            'order': content.order,
            'type': 'assignment',
            'content': content,
        })
    
    all_contents.sort(key=lambda x: x['order'])
    
    # Get next and previous modules
    modules = list(course.modules.order_by('order'))
    current_index = modules.index(module)
    prev_module = modules[current_index - 1] if current_index > 0 else None
    next_module = modules[current_index + 1] if current_index < len(modules) - 1 else None
    
    # Update last_accessed if enrolled
    if is_enrolled:
        enrollment = Enrollment.objects.get(student=request.user, course=course)
        enrollment.last_accessed = timezone.now()
        enrollment.save()
    
    context = {
        'course': course,
        'module': module,
        'all_contents': all_contents,
        'is_enrolled': is_enrolled,
        'prev_module': prev_module,
        'next_module': next_module,
    }
    
    return render(request, 'courses/module_detail.html', context)

@login_required
def content_detail(request, course_slug, module_id, content_type, content_id):
    """
    Show a specific content item (text, video, resource, or assignment)
    """
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if module is free preview or if user is enrolled
    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course, status__in=['active', 'completed']
    ).exists()
    
    if not (module.is_free_preview or is_enrolled):
        messages.error(request, _('You need to enroll in this course to access this content.'))
        return redirect('course_detail', course_slug=course.slug)
    
    # Get the specific content based on type
    content = None
    template = 'courses/content_detail.html'
    
    if content_type == 'text':
        content = get_object_or_404(TextContent, id=content_id, module=module)
    elif content_type == 'video':
        content = get_object_or_404(VideoContent, id=content_id, module=module)
    elif content_type == 'resource':
        content = get_object_or_404(ResourceContent, id=content_id, module=module)
    elif content_type == 'assignment':
        content = get_object_or_404(Assignment, id=content_id, module=module)
        template = 'courses/assignment_detail.html'
    else:
        messages.error(request, _('Invalid content type.'))
        return redirect('module_detail', course_slug=course.slug, module_id=module.id)
    
    # Mark as completed if enrolled
    if is_enrolled and request.method == 'POST' and 'mark_complete' in request.POST:
        enrollment = Enrollment.objects.get(student=request.user, course=course)
        
        # Create or update progress
        progress, created = Progress.objects.get_or_create(
            enrollment=enrollment,
            module=module,
            content_type=content_type,
            content_id=content_id,
            defaults={'completed': True}
        )
        
        if not created:
            progress.completed = True
            progress.save()
        
        # Update time_spent
        if 'time_spent' in request.POST:
            try:
                time_spent = int(request.POST.get('time_spent'))
                progress.time_spent += time_spent
                progress.save()
            except ValueError:
                pass
        
        # Update overall course completion percentage
        update_course_completion(enrollment)
        
        messages.success(request, _('Content marked as completed!'))
        return redirect('module_detail', course_slug=course.slug, module_id=module.id)
    
    # Check if this content is completed
    is_completed = False
    if is_enrolled:
        enrollment = Enrollment.objects.get(student=request.user, course=course)
        is_completed = Progress.objects.filter(
            enrollment=enrollment,
            module=module,
            content_type=content_type,
            content_id=content_id,
            completed=True
        ).exists()
    
    context = {
        'course': course,
        'module': module,
        'content': content,
        'content_type': content_type,
        'is_enrolled': is_enrolled,
        'is_completed': is_completed,
    }
    
    return render(request, template, context)

@login_required
def course_reviews(request, course_slug):
    """
    Show all reviews for a course
    """
    course = get_object_or_404(Course, slug=course_slug)
    reviews = course.reviews.all().order_by('-created_at')
    
    # Check if user can review
    can_review = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=course, status__in=['active', 'completed']
        ).exists()
        has_reviewed = Review.objects.filter(course=course, student=request.user).exists()
        can_review = is_enrolled and not has_reviewed
    
    context = {
        'course': course,
        'reviews': reviews,
        'can_review': can_review,
    }
    
    return render(request, 'courses/course_reviews.html', context)

@login_required
def add_review(request, course_slug):
    """
    Add a review for a course
    """
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is enrolled and hasn't already reviewed
    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course, status__in=['active', 'completed']
    ).exists()
    
    has_reviewed = Review.objects.filter(course=course, student=request.user).exists()
    
    if not is_enrolled:
        messages.error(request, _('You must be enrolled in this course to review it.'))
        return redirect('course_detail', course_slug=course.slug)
    
    if has_reviewed:
        messages.error(request, _('You have already reviewed this course.'))
        return redirect('course_reviews', course_slug=course.slug)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating or not comment:
            messages.error(request, _('Please provide both a rating and a comment.'))
            return redirect('add_review', course_slug=course.slug)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            messages.error(request, _('Rating must be between 1 and 5.'))
            return redirect('add_review', course_slug=course.slug)
        
        # Create the review
        Review.objects.create(
            course=course,
            student=request.user,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, _('Your review has been submitted. Thank you!'))
        return redirect('course_reviews', course_slug=course.slug)
    
    context = {
        'course': course,
    }
    
    return render(request, 'courses/add_review.html', context)

@login_required
def instructor_dashboard(request):
    """
    Instructor dashboard showing overview of courses and students
    """
    if not (request.user.is_instructor or request.user.is_staff):
        messages.error(request, _('You do not have permission to view the instructor dashboard.'))
        return redirect('dashboard')
    
    instructor_courses = Course.objects.filter(instructor=request.user)
    
    # Get enrollment stats
    total_students = 0
    course_stats = []
    
    for course in instructor_courses:
        enrollments = course.enrollments.all()
        student_count = enrollments.count()
        total_students += student_count
        
        active_count = enrollments.filter(status='active').count()
        completed_count = enrollments.filter(status='completed').count()
        
        avg_rating = course.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        review_count = course.reviews.count()
        
        course_stats.append({
            'course': course,
            'student_count': student_count,
            'active_count': active_count,
            'completed_count': completed_count,
            'avg_rating': avg_rating,
            'review_count': review_count,
        })
    
    context = {
        'total_courses': instructor_courses.count(),
        'total_students': total_students,
        'course_stats': course_stats,
    }
    
    return render(request, 'courses/instructor_dashboard.html', context)

# Helper functions
def update_course_completion(enrollment):
    """
    Update the completion percentage for an enrollment
    """
    course = enrollment.course
    modules = course.modules.all()
    
    total_content_count = 0
    completed_content_count = 0
    
    for module in modules:
        # Count all content items
        text_count = TextContent.objects.filter(module=module).count()
        video_count = VideoContent.objects.filter(module=module).count()
        resource_count = ResourceContent.objects.filter(module=module).count()
        assignment_count = Assignment.objects.filter(module=module).count()
        
        module_content_count = text_count + video_count + resource_count + assignment_count
        total_content_count += module_content_count
        
        # Count completed content items
        completed_count = Progress.objects.filter(
            enrollment=enrollment,
            module=module,
            completed=True
        ).count()
        
        completed_content_count += completed_count
    
    # Calculate percentage
    if total_content_count > 0:
        completion_percentage = int((completed_content_count / total_content_count) * 100)
    else:
        completion_percentage = 0
    
    # Update enrollment
    enrollment.completion_percentage = completion_percentage
    
    # Mark as completed if 100%
    if completion_percentage == 100 and enrollment.status == 'active':
        enrollment.status = 'completed'
        enrollment.date_completed = timezone.now()
    
    enrollment.save()
    
    return completion_percentage
