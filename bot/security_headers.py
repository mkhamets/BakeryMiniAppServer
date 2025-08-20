"""
Security Headers Middleware for AioHTTP
Adds comprehensive security headers to all HTTP responses.
"""

import hashlib
import logging
from typing import Callable, Awaitable
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware:
    """Middleware to add security headers to all responses."""
    
    def __init__(self):
        # Content Security Policy - restrictive but allows Telegram WebApp functionality
        self.csp_policy = (
            "default-src 'self' https://telegram.org; "
            "script-src 'self' 'unsafe-inline' https://telegram.org; "
            "style-src 'self' 'unsafe-inline' https://telegram.org; "
            "img-src 'self' data: https: http:; "
            "font-src 'self' https://telegram.org; "
            "connect-src 'self' https://telegram.org; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests"
        )
        
        # Permissions Policy - restrict sensitive APIs
        self.permissions_policy = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "encrypted-media=(), "
            "picture-in-picture=()"
        )
    
    async def __call__(self, request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
        """Add security headers to response."""
        response = await handler(request)
        
        # Security headers
        response.headers.update({
            # Prevent clickjacking
            'X-Frame-Options': 'DENY',
            
            # Prevent MIME type sniffing
            'X-Content-Type-Options': 'nosniff',
            
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Content Security Policy
            'Content-Security-Policy': self.csp_policy,
            
            # Permissions Policy
            'Permissions-Policy': self.permissions_policy,
            
            # XSS Protection (legacy but still useful)
            'X-XSS-Protection': '1; mode=block',
            
            # Prevent caching of sensitive data
            'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })
        
        # Add HSTS header only for HTTPS requests
        if request.scheme == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response

def create_content_hash(content: bytes) -> str:
    """Create a stable content hash for ETag generation."""
    return hashlib.md5(content).hexdigest()

# Global middleware instance
security_headers_middleware = SecurityHeadersMiddleware()
