from django.http import HttpResponse

def hello_world(request):
    """Simple function-based view to verify basic Django functionality"""
    return HttpResponse("Hello, World! SkillForge is working at a basic level.")
