"""
Security Middleware
セキュリティミドルウェア
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware
    レート制限ミドルウェア
    """
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # In-memory rate limit tracking (use Redis in production)
        self.minute_requests = defaultdict(list)
        self.hour_requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)
        
        # Check rate limits
        current_time = datetime.utcnow()
        
        # Clean old entries
        self._clean_old_entries(client_id, current_time)
        
        # Check minute limit
        minute_count = len(self.minute_requests[client_id])
        if minute_count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded (minute) for client: {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                }
            )
        
        # Check hour limit
        hour_count = len(self.hour_requests[client_id])
        if hour_count >= self.requests_per_hour:
            logger.warning(f"Rate limit exceeded (hour) for client: {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Hourly rate limit exceeded. Please try again later.",
                    "retry_after": 3600
                }
            )
        
        # Record request
        self.minute_requests[client_id].append(current_time)
        self.hour_requests[client_id].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            self.requests_per_minute - minute_count - 1
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            self.requests_per_hour - hour_count - 1
        )
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get user ID from JWT token
        user = getattr(request.state, "user", None)
        if user:
            return f"user_{user.id}"
        
        # Fallback to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"
    
    def _clean_old_entries(self, client_id: str, current_time: datetime):
        """Remove old entries outside the time window"""
        # Clean minute entries
        minute_ago = current_time - timedelta(minutes=1)
        self.minute_requests[client_id] = [
            t for t in self.minute_requests[client_id] if t > minute_ago
        ]
        
        # Clean hour entries
        hour_ago = current_time - timedelta(hours=1)
        self.hour_requests[client_id] = [
            t for t in self.hour_requests[client_id] if t > hour_ago
        ]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to responses
    セキュリティヘッダーを追加
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests for security audit
    セキュリティ監査のためのリクエストログ
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} "
                f"processed in {process_time:.3f}s"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"Error: {str(e)}"
            )
            raise


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Basic input validation and sanitization
    入力検証とサニタイゼーション
    """
    
    SUSPICIOUS_PATTERNS = [
        "script>",
        "javascript:",
        "onerror=",
        "onclick=",
        "<iframe",
        "eval(",
        "exec(",
        "__import__",
        "'; DROP",
        "' OR '1'='1",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Check query parameters
        query_string = str(request.url.query).lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.lower() in query_string:
                logger.warning(
                    f"Suspicious pattern detected in query: {pattern} "
                    f"from {request.client.host if request.client else 'unknown'}"
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request parameters"}
                )
        
        # Check path for suspicious patterns
        path = str(request.url.path).lower()
        suspicious_paths = ["../", "..\\", "/etc/", "c:\\", ".env", "config"]
        for suspicious in suspicious_paths:
            if suspicious in path:
                logger.warning(
                    f"Suspicious path detected: {path} "
                    f"from {request.client.host if request.client else 'unknown'}"
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request path"}
                )
        
        return await call_next(request)
