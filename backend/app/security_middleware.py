"""
Additional security middleware
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib
import hmac

class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    """Add Content Security Policy headers"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add CSP header
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.firebase.com https://*.firebaseio.com;"
        )
        
        response.headers["Content-Security-Policy"] = csp
        return response

class IntegrityCheckMiddleware(BaseHTTPMiddleware):
    """Check request integrity using HMAC"""
    
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key.encode()
    
    async def dispatch(self, request: Request, call_next):
        # Skip for GET requests
        if request.method == "GET":
            return await call_next(request)
        
        # Check for integrity header
        integrity_header = request.headers.get("X-Integrity-Check")
        if integrity_header and request.method in ["POST", "PUT", "DELETE"]:
            # Verify integrity (simplified example)
            # In production, implement proper HMAC verification
            pass
        
        return await call_next(request)
