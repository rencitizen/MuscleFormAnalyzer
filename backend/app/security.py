"""
Security configuration and best practices
"""
from typing import List

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "default": "100/minute",
    "auth": "10/minute",
    "upload": "20/minute"
}

# File upload restrictions
ALLOWED_UPLOAD_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "video": [".mp4", ".avi", ".mov", ".webm"]
}

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# Input validation
MAX_STRING_LENGTH = 1000
MAX_TEXT_LENGTH = 10000

# Session configuration
SESSION_TIMEOUT = 24 * 60 * 60  # 24 hours
REFRESH_TOKEN_EXPIRY = 30 * 24 * 60 * 60  # 30 days

# Password policy (if implementing local auth)
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL = True

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Validate file extension"""
    ext = Path(filename).suffix.lower()
    return ext in allowed_types

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal"""
    import re
    # Remove any directory components
    filename = os.path.basename(filename)
    # Remove any non-alphanumeric characters except dots and dashes
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename

def validate_url(url: str) -> bool:
    """Validate URL format"""
    from urllib.parse import urlparse
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
