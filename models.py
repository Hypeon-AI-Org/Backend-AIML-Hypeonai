"""User models for Hypeon AI Authentication System."""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    picture: Optional[str] = None
    auth_provider: AuthProvider
    google_id: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None


class UserInDB(UserBase):
    id: str
    password_hash: Optional[str] = None
    created_at: datetime


class UserResponse(UserBase):
    id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str
    email: str
    provider: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str