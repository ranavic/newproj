from django.http import HttpResponse

def test_view(request):
    """A simple test view to check if basic routing works."""
    return HttpResponse("SkillForge basic test view is working!")
