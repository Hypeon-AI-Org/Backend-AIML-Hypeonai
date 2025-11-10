"""Authentication dependency for Hypeon AI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from models import UserInDB, TokenData
from jwt_utils import decode_access_token
from user_crud import get_user_by_email


security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """Get current user from JWT token."""
    token = credentials.credentials
    token_data: TokenData = decode_access_token(token)
    
    user = await get_user_by_email(token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def auth_required_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """Dependency for requiring authentication."""
    return await get_current_user(credentials)