from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core import events
from app.utils.security import decode_token
from app.models.user_model import UserInDB
from bson import ObjectId
from jose import JWTError
from typing import Optional

# Security scheme for Bearer token authentication
# Use auto_error=False so missing Authorization header doesn't raise immediately.
# This allows `get_current_user_flexible` to fall back to cookie-based auth when
# the Authorization header is absent.
security = HTTPBearer(auto_error=False)

async def get_db():
    """Dependency to get database connection instance"""
    return events.db

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)):
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials containing the Bearer token
        db: Database connection instance
        
    Returns:
        UserInDB: The authenticated user's data
        
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        payload = decode_token(token)
        # Verify this is an access token
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type - expected access token"
            )
            
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - missing user ID"
            )
        
        # Convert sub to ObjectId and fetch user
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(sub)})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return UserInDB(**user_doc, id=str(user_doc["_id"]))
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )

async def get_current_user_from_cookie(request: Request, db=Depends(get_db)):
    """
    Dependency to get current authenticated user from refresh token in cookie.
    
    Args:
        request: FastAPI request object to access cookies
        db: Database connection instance
        
    Returns:
        UserInDB: The authenticated user's data
        
    Raises:
        HTTPException: If refresh token is invalid, expired, or user not found
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")
    
    try:
        payload = decode_token(refresh_token)
        # Verify this is a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
        # Get user from database
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
            
        return UserInDB(**user_doc, id=str(user_doc["_id"]))
    except JWTError:
        # Handle JWT-specific errors (invalid signature, expired, etc.)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except Exception as e:
        # Handle specific database errors
        if "ObjectId" in str(e):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
        # Handle unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_current_user_flexible(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db=Depends(get_db)):
    """
    Flexible authentication dependency that accepts:
    1. Bearer token in Authorization header (primary)
    2. Refresh token in HTTP-only cookie (fallback)
    
    This allows endpoints to work with both standard Bearer token authentication
    and cookie-based authentication for better frontend integration.
    
    Args:
        request: FastAPI request object to access cookies
        credentials: Optional HTTP Authorization credentials containing Bearer token
        db: Database connection instance
        
    Returns:
        UserInDB: The authenticated user's data
        
    Raises:
        HTTPException: If no valid authentication is provided
    """
    # First, try Bearer token authentication
    if credentials and credentials.credentials:
        try:
            token = credentials.credentials
            payload = decode_token(token)
            
            # Verify this is an access token
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type - expected access token"
                )
                
            sub = payload.get("sub")
            if not sub:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token - missing user ID"
                )
            
            # Convert sub to ObjectId and fetch user
            try:
                user_doc = await db.users.find_one({"_id": ObjectId(sub)})
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format"
                )
            
            if user_doc:
                return UserInDB(**user_doc, id=str(user_doc["_id"]))
        except HTTPException:
            raise
        except Exception:
            pass  # Fall through to cookie authentication
    
    # Fall back to refresh token in cookie
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            
            # Verify this is a refresh token
            if payload.get("type") == "refresh":
                user_id = payload.get("sub")
                if user_id:
                    try:
                        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
                        if user_doc:
                            return UserInDB(**user_doc, id=str(user_doc["_id"]))
                    except Exception:
                        pass
        except Exception:
            pass
    
    # No valid authentication method worked
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )