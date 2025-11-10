"""Authentication router for Hypeon AI."""

from fastapi import APIRouter, HTTPException, status, Response, Depends
from fastapi.responses import RedirectResponse
from typing import Dict, Any
import logging
from models import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    Token,
    UserCreate,
    AuthProvider
)
from jwt_utils import create_access_token
from user_crud import (
    create_user,
    authenticate_user,
    get_user_by_email,
    get_user_by_google_id
)
from auth_dependency import auth_required_dependency
from google_oauth import (
    get_google_auth_url,
    exchange_code_for_token,
    get_google_user_info,
    FRONTEND_REDIRECT_URI
)
from datetime import timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token)
async def signup(signup_request: SignupRequest) -> Token:
    """Sign up a new user with local authentication."""
    # Check if user already exists
    existing_user = await get_user_by_email(signup_request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    user_data = UserCreate(
        name=signup_request.name,
        email=signup_request.email,
        auth_provider=AuthProvider.LOCAL
    )
    
    user = await create_user(user_data, signup_request.password)
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "provider": user.auth_provider
        },
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login(login_request: LoginRequest) -> Token:
    """Log in an existing user with local authentication."""
    user = await authenticate_user(login_request.email, login_request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "provider": user.auth_provider
        },
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(auth_required_dependency)) -> UserResponse:
    """Get current user information."""
    return current_user


@router.get("/google/login")
async def google_login():
    """Redirect to Google OAuth login."""
    google_auth_url = await get_google_auth_url()
    return RedirectResponse(google_auth_url)


@router.get("/google/callback")
async def google_callback(code: str):
    """Handle Google OAuth callback."""
    try:
        # Exchange code for token
        token_response = await exchange_code_for_token(code)
        access_token = token_response["access_token"]
        
        # Get user info from Google
        google_user_info = await get_google_user_info(access_token)
        
        # Check if user exists
        user = await get_user_by_google_id(google_user_info["id"])
        
        if not user:
            # Check if user exists with the same email
            user = await get_user_by_email(google_user_info["email"])
            
            if user:
                # Update existing user with Google ID
                # (Implementation would go here if needed)
                pass
            else:
                # Create new user
                user_data = UserCreate(
                    name=google_user_info["name"],
                    email=google_user_info["email"],
                    picture=google_user_info.get("picture"),
                    auth_provider=AuthProvider.GOOGLE,
                    google_id=google_user_info["id"]
                )
                
                user = await create_user(user_data)
        
        # Create access token
        access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
        access_token = create_access_token(
            data={
                "user_id": user.id,
                "email": user.email,
                "provider": user.auth_provider
            },
            expires_delta=access_token_expires
        )
        
        # Redirect to frontend with token
        redirect_url = f"{FRONTEND_REDIRECT_URI}?token={access_token}"
        return RedirectResponse(redirect_url)
        
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google"
        )