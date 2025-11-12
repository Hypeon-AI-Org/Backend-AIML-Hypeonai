from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserInDB(BaseModel):
    """Schema for user data stored in the database."""
    id: Optional[str]
    name: Optional[str]
    email: EmailStr
    passwordHash: Optional[str]
    googleId: Optional[str]
    role: Optional[str] = "user"
    resetPasswordToken: Optional[str]
    resetPasswordExpires: Optional[datetime]
    createdAt: Optional[datetime]