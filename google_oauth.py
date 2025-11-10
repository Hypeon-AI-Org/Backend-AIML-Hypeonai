"""Google OAuth utilities for Hypeon AI Authentication System."""

import os
import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException, status


# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
FRONTEND_REDIRECT_URI = os.getenv("FRONTEND_REDIRECT_URI", "http://localhost:3000/dashboard")


async def get_google_auth_url() -> str:
    """Generate Google OAuth authorization URL."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?client_id={}"
        "&redirect_uri={}"
        "&scope=openid%20email%20profile"
        "&response_type=code"
        "&access_type=offline"
    ).format(GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI)
    
    return google_auth_url


async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """Exchange authorization code for access token."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": GOOGLE_REDIRECT_URI
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token"
            )
        
        return response.json()


async def get_google_user_info(access_token: str) -> Dict[str, Any]:
    """Get user info from Google using access token."""
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(user_info_url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )
        
        return response.json()