from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserInDB(BaseModel):
    """Schema for user data stored in the database."""
    model_config = ConfigDict(extra='ignore')  # Ignore extra fields not in model
    
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    passwordHash: Optional[str] = None
    googleId: Optional[str] = None
    role: Optional[str] = "user"
    resetPasswordToken: Optional[str] = None
    resetPasswordExpires: Optional[datetime] = None
    createdAt: Optional[datetime] = None