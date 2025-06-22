"""
Custom middleware for the API
"""
import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import gzip
from io import BytesIO

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or get request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store in request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """Add response time to headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        
        return response

class StandardResponseMiddleware(BaseHTTPMiddleware):
    """Standardize API responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            
            # Only process JSON responses
            if response.headers.get("content-type", "").startswith("application/json"):
                # For successful responses, ensure standard format
                if 200 <= response.status_code < 300:
                    # Response is already in correct format, pass through
                    pass
            
            return response
            
        except Exception as e:
            # This should be handled by exception handlers
            raise

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add CSP for production
        if request.app.state.environment == "production":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline';"
            )
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting in development
        if request.app.state.environment == "development":
            return await call_next(request)
        
        # Get client identifier
        client_id = request.client.host if request.client else "unknown"
        
        # Simple in-memory rate limiting (use Redis in production)
        current_time = time.time()
        
        if client_id not in self.clients:
            self.clients[client_id] = []
        
        # Remove old entries
        self.clients[client_id] = [
            timestamp for timestamp in self.clients[client_id]
            if current_time - timestamp < self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_id]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Rate Limit Exceeded",
                    "detail": f"Maximum {self.calls} requests per {self.period} seconds",
                    "code": "RATE_LIMIT_EXCEEDED"
                },
                headers={"Retry-After": str(self.period)}
            )
        
        # Record this request
        self.clients[client_id].append(current_time)
        
        # Clean up old client entries periodically
        if len(self.clients) > 1000:
            self.clients = {
                k: v for k, v in self.clients.items()
                if len(v) > 0
            }
        
        return await call_next(request)

class GZipMiddleware(BaseHTTPMiddleware):
    """Compress responses with gzip"""
    
    def __init__(self, app, minimum_size: int = 1000):
        super().__init__(app)
        self.minimum_size = minimum_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        
        response = await call_next(request)
        
        # Only compress if client accepts gzip and response is large enough
        if "gzip" not in accept_encoding.lower():
            return response
            
        # Only compress JSON and text responses
        content_type = response.headers.get("content-type", "")
        if not any(ct in content_type for ct in ["application/json", "text/"]):
            return response
            
        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
            
        # Check size threshold
        if len(body) < self.minimum_size:
            # Return original response
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Compress body
        compressed = gzip.compress(body)
        
        # Update headers
        headers = dict(response.headers)
        headers["content-encoding"] = "gzip"
        headers["content-length"] = str(len(compressed))
        
        return Response(
            content=compressed,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )