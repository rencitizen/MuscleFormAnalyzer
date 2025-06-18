"""
Custom exceptions and error handlers for the API
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    request_id: Optional[str] = None

class APIException(HTTPException):
    """Base API exception with standardized error response"""
    def __init__(
        self,
        status_code: int,
        error: str,
        detail: Optional[str] = None,
        code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error = error
        self.code = code

# Specific exception classes
class AuthenticationException(APIException):
    """Authentication failed"""
    def __init__(self, detail: str = "認証に失敗しました"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="Authentication Failed",
            detail=detail,
            code="AUTH_FAILED"
        )

class AuthorizationException(APIException):
    """Authorization failed"""
    def __init__(self, detail: str = "権限がありません"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="Authorization Failed",
            detail=detail,
            code="AUTH_FORBIDDEN"
        )

class NotFoundException(APIException):
    """Resource not found"""
    def __init__(self, resource: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error=f"{resource} Not Found",
            detail=detail or f"指定された{resource}が見つかりません",
            code="NOT_FOUND"
        )

class ValidationException(APIException):
    """Validation error"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="Validation Error",
            detail=detail,
            code="VALIDATION_ERROR"
        )

class BadRequestException(APIException):
    """Bad request"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="Bad Request",
            detail=detail,
            code="BAD_REQUEST"
        )

class ConflictException(APIException):
    """Resource conflict"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error="Conflict",
            detail=detail,
            code="CONFLICT"
        )

class RateLimitException(APIException):
    """Rate limit exceeded"""
    def __init__(self, detail: str = "リクエスト数が制限を超えました"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error="Rate Limit Exceeded",
            detail=detail,
            code="RATE_LIMIT_EXCEEDED",
            headers={"Retry-After": "60"}
        )

class ServiceUnavailableException(APIException):
    """Service temporarily unavailable"""
    def __init__(self, detail: str = "サービスが一時的に利用できません"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error="Service Unavailable",
            detail=detail,
            code="SERVICE_UNAVAILABLE"
        )

# Error handlers
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle API exceptions"""
    request_id = request.headers.get("X-Request-ID", "")
    
    logger.error(
        f"API Exception: {exc.error} - {exc.detail}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "error_code": exc.code
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error,
            detail=exc.detail,
            code=exc.code,
            request_id=request_id
        ).dict(),
        headers=exc.headers
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions"""
    request_id = request.headers.get("X-Request-ID", "")
    
    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    # Map status codes to error messages
    error_map = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        422: "Validation Error",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable"
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=error_map.get(exc.status_code, "Error"),
            detail=str(exc.detail),
            request_id=request_id
        ).dict()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors"""
    request_id = request.headers.get("X-Request-ID", "")
    
    # Extract validation errors
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    detail = "入力データが無効です。" + " ".join(errors)
    
    logger.warning(
        f"Validation Error: {detail}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            detail=detail,
            code="VALIDATION_ERROR",
            request_id=request_id
        ).dict()
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    request_id = request.headers.get("X-Request-ID", "")
    
    logger.exception(
        f"Unexpected error: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Don't expose internal errors in production
    detail = "内部エラーが発生しました" if request.app.state.environment == "production" else str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=detail,
            code="INTERNAL_ERROR",
            request_id=request_id
        ).dict()
    )