from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any, List, Dict
from datetime import datetime

# Auth
class UserCreate(BaseModel):
    """Schema for user registration data."""
    name: Optional[str]
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Schema for user login (email and password only)."""
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

class ProductOut(BaseModel):
    """Schema for product data returned in responses."""
    id: str
    title: Optional[str] = None
    product_type: Optional[str] = Field(None, alias="Product Type")
    category: Optional[str] = Field(None, alias="Category")
    color: Optional[str] = None
    g_id: Optional[str] = Field(None, alias="g:id")
    product_name: Optional[str] = Field(None, alias="Product Name")
    hype_score: Optional[float] = Field(None, alias="Hype Score")
    weekly_growth: Optional[str] = Field(None, alias="Weekly Growth")
    monthly_growth: Optional[str] = Field(None, alias="Monthly growth")
    sales: Optional[str] = Field(None, alias="Sales")
    g_image_link: Optional[str] = Field(None, alias="g:image_link")
    g_additional_image_link: Optional[str] = Field(None, alias="g:additional_image_link")
    niche: Optional[str] = None
    region: Optional[str] = None
    
    class Config:
        populate_by_name = True  # Allow both field name and alias

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
