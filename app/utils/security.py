from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from typing import Union, Dict, Any

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        password (str): The plaintext password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a hashed password.
    
    Args:
        plain (str): The plaintext password to verify
        hashed (str): The hashed password to compare against
        
    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: Union[str, dict], expires_delta: timedelta | None = None):
    """
    Create a JWT access token.
    
    Args:
        subject (str | dict): The subject of the token (typically user ID)
        expires_delta (timedelta | None): Token expiration time delta
        
    Returns:
        str: The encoded JWT token
    """
    to_encode: Dict[str, Any] = {"sub": subject, "type": "access"}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(subject: Union[str, dict], expires_delta: timedelta | None = None):
    """
    Create a JWT refresh token.
    
    Args:
        subject (str | dict): The subject of the token (typically user ID)
        expires_delta (timedelta | None): Token expiration time delta (default: 7 days)
        
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode: Dict[str, Any] = {"sub": subject, "type": "refresh"}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # Refresh token valid for 7 days
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str):
    """
    Decode a JWT token.
    
    Args:
        token (str): The JWT token to decode
        
    Returns:
        dict: The decoded token payload
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])