from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any, List, Dict
from datetime import datetime

# Auth
class UserCreate(BaseModel):
    """Schema for user registration data."""
    name: Optional[str]
    email: EmailStr
    password: str

class UserOut(BaseModel):
    """Schema for user data returned in responses."""
    id: str
    name: Optional[str]
    email: EmailStr

class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserOut

# Password reset
class ForgotPasswordIn(BaseModel):
    """Schema for forgot password request."""
    email: EmailStr

class ResetPasswordIn(BaseModel):
    """Schema for password reset request."""
    token: str
    new_password: str

# Products
class ProductIn(BaseModel):
    """Schema for product creation data."""
    title: str
    platform: str
    niche: str
    region: str
    hypeScore: float = 0
    growthWeekly: Optional[float] = None
    growthMonthly: Optional[float] = None
    metadata: Optional[Any] = None

class ProductOut(ProductIn):
    """Schema for product data returned in responses."""
    id: str

# Saved Search
class SavedSearchIn(BaseModel):
    """Schema for saved search creation data."""
    name: Optional[str]
    params: dict
    snapshot: Optional[List[dict]] = None
    notes: Optional[str] = None

class SavedSearchOut(BaseModel):
    """Schema for saved search data returned in responses."""
    id: str
    userId: str
    name: Optional[str]
    params: dict
    createdAt: datetime
    resultSnapshot: Optional[List[dict]] = None

# User Activity Tracking
class UserActivity(BaseModel):
    """Schema for user activity tracking."""
    userId: str
    action: str
    params: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
