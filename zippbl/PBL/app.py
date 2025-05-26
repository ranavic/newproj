def application(environ, start_response):
    """Minimal WSGI application to test basic server functionality"""
    status = '200 OK'
    output = b'SkillForge minimal test application is working!'
    
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(output)))
    ]
    
    start_response(status, response_headers)
    return [output]
