#!/usr/bin/env python3
"""
Simple WSGI test application
"""

def application(environ, start_response):
    """Simple WSGI application for testing"""
    status = '200 OK'
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Access-Control-Allow-Origin', '*'),
    ]
    
    response_body = b"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WSGI Test</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>WSGI Test Successful!</h1>
        <p>If you see this, WSGI is working correctly.</p>
        <p>Path: """ + environ.get('PATH_INFO', '/').encode('utf-8') + b"""</p>
        <p>Method: """ + environ.get('REQUEST_METHOD', 'GET').encode('utf-8') + b"""</p>
    </body>
    </html>
    """
    
    start_response(status, headers)
    return [response_body]
