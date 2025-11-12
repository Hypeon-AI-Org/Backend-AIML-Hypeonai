from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from app.utils.logger import logger
import os

# Check if we're in a testing environment
if os.getenv("TESTING") == "true":
    # Use a more aggressive rate limit for testing
    AUTH_RATE_LIMIT = "2/minute"  # 2 requests per minute for testing
    PASSWORD_RESET_RATE_LIMIT = "1/hour"  # 1 password reset request per hour for testing
    # Use a simple key function for testing
    limiter = Limiter(key_func=lambda: "test_key")
else:
    # Production rate limits
    AUTH_RATE_LIMIT = "5/minute"  # 5 requests per minute
    PASSWORD_RESET_RATE_LIMIT = "3/hour"  # 3 password reset requests per hour
    # Use IP address as the key function for rate limiting
    limiter = Limiter(key_func=get_remote_address)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    
    Args:
        request (Request): The incoming request
        exc (RateLimitExceeded): The rate limit exceeded exception
        
    Returns:
        Response: A JSON response with rate limit error information
    """
    logger.warning(f"Rate limit exceeded for IP: {get_remote_address(request)}")
    return Response(
        content='{"detail": "Rate limit exceeded. Please try again later."}',
        status_code=429,
        media_type="application/json"
    )