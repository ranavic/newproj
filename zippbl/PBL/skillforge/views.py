from django.shortcuts import render

def home(request):
    """
    View for the home page
    """
    return render(request, 'home.html')

def base(request):
    """
    View for the home page
    """
    return render(request, 'base.html')

def dashboard_view(request):
    streak = request.user.streak_days if request.user.is_authenticated else 0
    streak_mod = streak % 7
    return render(request, 'dashboard/dashboard.html', {
        'user': request.user,
        'streak_mod': streak_mod
    })

def terms(request):
    """
    View for the terms of service page
    """
    return render(request, 'terms.html')

def privacy(request):
    """
    View for the privacy policy page
    """
    return render(request, 'privacy.html')
