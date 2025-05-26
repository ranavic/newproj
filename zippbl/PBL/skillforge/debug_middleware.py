import sys
import traceback
from django.http import HttpResponse

class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            return HttpResponse(f"<pre>DEBUG ERROR:\n{error_details}</pre>", content_type="text/html", status=500)
