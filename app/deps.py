from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core import events
from app.utils.security import decode_token
from app.models.user_model import UserInDB
from bson import ObjectId
from jose import JWTError

# Security scheme for Bearer token authentication
security = HTTPBearer()

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
    token = credentials.credentials
    try:
        payload = decode_token(token)
        # Verify this is an access token
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # sub may be user id string
        user_doc = await db.users.find_one({"_id": ObjectId(sub)})
        if not user_doc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return UserInDB(**user_doc, id=str(user_doc["_id"]))
    except JWTError:
        # Handle JWT-specific errors (invalid signature, expired, etc.)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        # Handle specific database errors
        if "ObjectId" in str(e):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
        # Handle unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

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