from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from datetime import timedelta, datetime
from app.schemas import UserCreate, UserLogin, TokenResponse, ForgotPasswordIn, ResetPasswordIn, UserOut
from app.core import events
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.deps import get_current_user, get_current_user_flexible
from app.utils.logger import logger
from app.utils.activity_tracker import log_user_activity
from app.utils.rate_limiter import limiter, AUTH_RATE_LIMIT, PASSWORD_RESET_RATE_LIMIT
import secrets
from bson import ObjectId
from app.utils.emailer import send_reset_email

from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from google.auth.exceptions import GoogleAuthError
from pydantic import BaseModel

router = APIRouter()

def is_email_whitelisted(email: str) -> bool:
    """
    Check if an email is whitelisted for login access.
    
    Args:
        email (str): Email address to check
        
    Returns:
        bool: True if whitelist is disabled or email is whitelisted, False otherwise
    """
    if not settings.ENABLE_EMAIL_WHITELIST:
        return True
    
    email_lower = email.lower().strip()
    return email_lower in settings.WHITELISTED_EMAILS

# Signup
@router.post("/signup", response_model=TokenResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def signup(request: Request, data: UserCreate, response: Response):
    """
    Register a new user account.
    
    Args:
        data (UserCreate): User registration data including name, email, and password
        response (Response): FastAPI response object for setting cookies
        
    Returns:
        TokenResponse: JWT access token, refresh token, and user information
        
    Raises:
        HTTPException: If email is already in use or not whitelisted
    """
    logger.info(f"Signup attempt for email: {data.email}")
    
    # Check email whitelist
    if not is_email_whitelisted(data.email):
        logger.warning(f"Signup failed - email not whitelisted: {data.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not authorized for access")
    
    db = events.db
    existing = await db.users.find_one({"email": data.email})
    if existing:
        logger.warning(f"Signup failed - email already in use: {data.email}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    
    pw_hash = hash_password(data.password)
    doc = {
        "name": data.name,
        "email": data.email,
        "passwordHash": pw_hash,
        "createdAt": datetime.utcnow()
    }
    
    try:
        res = await db.users.insert_one(doc)
        user_id = str(res.inserted_id)
        logger.info(f"Successful signup for user: {user_id} ({data.email})")
        
        # Log user activity
        await log_user_activity(user_id, "signup", {"email": data.email})
    except Exception as e:
        logger.error(f"Database error during signup for {data.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")
    
    # Create tokens
    access_token = create_access_token(user_id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(user_id)
    
    # Set refresh token in httpOnly cookie. Use SameSite=None for cross-site cookie
    if settings.FRONTEND_URL.startswith("https://"):
        samesite_val = "none"
        secure_cookie = True
    elif "localhost" in settings.FRONTEND_URL:
        samesite_val = "lax"
        secure_cookie = False
    else:
        samesite_val = "none"
        secure_cookie = True

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60*60*24*7,
        path="/",            # FIX: Cookie available to all paths
        samesite=samesite_val,
        secure=secure_cookie,
    )
    
    user_out = UserOut(id=user_id, name=data.name, email=data.email)
    logger.info(f"Tokens generated for user: {user_id}")
    return {"access_token": access_token, "refresh_token": refresh_token, "user": user_out, "token_type": "bearer"}

# Login
@router.post("/login", response_model=TokenResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def login(request: Request, data: UserLogin, response: Response):
    """
    Authenticate a user with email and password.
    
    Args:
        data (UserCreate): User login credentials (email and password)
        response (Response): FastAPI response object for setting cookies
        
    Returns:
        TokenResponse: JWT access token, refresh token, and user information
        
    Raises:
        HTTPException: If credentials are invalid or email is not whitelisted
    """
    logger.info(f"Login attempt for email: {data.email}")
    
    # Check email whitelist
    if not is_email_whitelisted(data.email):
        logger.warning(f"Login failed - email not whitelisted: {data.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not authorized for access")
    
    db = events.db
    user = await db.users.find_one({"email": data.email})
    if not user or not user.get("passwordHash"):
        logger.warning(f"Login failed - invalid credentials for email: {data.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not verify_password(data.password, user["passwordHash"]):
        logger.warning(f"Login failed - invalid password for email: {data.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    user_id = str(user["_id"])
    logger.info(f"Successful login for user: {user_id} ({data.email})")
    
    # Log user activity
    await log_user_activity(user_id, "login", {"method": "email"})
    
    # Create tokens
    access_token = create_access_token(user_id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(user_id)
    
    # Set refresh token in httpOnly cookie. Use SameSite=None for cross-site cookie
    if settings.FRONTEND_URL.startswith("https://"):
        samesite_val = "none"
        secure_cookie = True
    elif "localhost" in settings.FRONTEND_URL:
        samesite_val = "lax"
        secure_cookie = False
    else:
        samesite_val = "none"
        secure_cookie = True

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60*60*24*7,
        path="/",            # FIX: Cookie available to all paths
        samesite=samesite_val,
        secure=secure_cookie,
    )
    
    user_out = UserOut(id=user_id, name=user.get("name"), email=user.get("email"))
    # update last login
    try:
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"lastLoginAt": datetime.utcnow()}})
        logger.info(f"Last login updated for user: {user_id}")
    except Exception as e:
        logger.error(f"Failed to update last login for user {user_id}: {str(e)}")
    
    logger.info(f"Tokens generated for user: {user_id}")
    return {"access_token": access_token, "refresh_token": refresh_token, "user": user_out, "token_type": "bearer"}

@router.post("/google", response_model=TokenResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def google_login(request: Request, payload: dict, response: Response):
    """
    Authenticate a user with Google OAuth2 ID token.
    
    Args:
        payload (dict): Contains the Google ID token
        response (Response): FastAPI response object for setting cookies
        
    Returns:
        TokenResponse: JWT access token, refresh token, and user information
        
    Raises:
        HTTPException: If Google token is invalid or authentication fails
    """
    logger.info("Google login attempt")
    
    id_token_str = payload.get("idToken") or payload.get("id_token")
    if not id_token_str:
        logger.warning("Google login failed - missing idToken")
        raise HTTPException(status_code=400, detail="Missing idToken")
    
    try:
        idinfo = id_token.verify_oauth2_token(id_token_str, grequests.Request(), settings.GOOGLE_CLIENT_ID)
        logger.info(f"Google token verified for email: {idinfo.get('email')}")
    except GoogleAuthError as e:
        logger.warning(f"Google login failed - invalid Google token: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")
    except ValueError as e:
        logger.warning(f"Google login failed - invalid token format: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid token format: {str(e)}")
    except Exception as e:
        logger.error(f"Google login failed - internal error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error during Google authentication: {str(e)}")
    
    email = idinfo.get("email")
    name = idinfo.get("name")
    sub = idinfo.get("sub")
    db = events.db
    
    # Check email whitelist
    if not is_email_whitelisted(email):
        logger.warning(f"Google login failed - email not whitelisted: {email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not authorized for access")
    
    logger.info(f"Looking up user with email: {email}")
    user = await db.users.find_one({"email": email})
    
    if not user:
        # create
        logger.info(f"Creating new user for email: {email}")
        doc = {"email": email, "name": name, "googleId": sub, "createdAt": datetime.utcnow()}
        try:
            r = await db.users.insert_one(doc)
            user_id = str(r.inserted_id)
            logger.info(f"New user created with ID: {user_id}")
            
            # Log user activity
            await log_user_activity(user_id, "signup", {"email": email, "method": "google"})
        except Exception as e:
            logger.error(f"Failed to create user for {email}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")
    else:
        # update googleId if missing
        if not user.get("googleId"):
            logger.info(f"Updating Google ID for existing user: {email}")
            try:
                await db.users.update_one({"_id": user["_id"]}, {"$set": {"googleId": sub}})
                logger.info(f"Google ID updated for user: {str(user['_id'])}")
            except Exception as e:
                logger.error(f"Failed to update Google ID for user {str(user['_id'])}: {str(e)}")
        user_id = str(user["_id"])
        logger.info(f"Existing user logged in with ID: {user_id}")
        
        # Log user activity
        await log_user_activity(user_id, "login", {"method": "google"})
    
    # Create tokens
    access_token = create_access_token(user_id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(user_id)
    
    # Set refresh token in httpOnly cookie. Use SameSite=None for cross-site cookie
    if settings.FRONTEND_URL.startswith("https://"):
        samesite_val = "none"
        secure_cookie = True
    elif "localhost" in settings.FRONTEND_URL:
        samesite_val = "lax"
        secure_cookie = False
    else:
        samesite_val = "none"
        secure_cookie = True

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60*60*24*7,
        path="/",            # FIX: Cookie available to all paths
        samesite=samesite_val,
        secure=secure_cookie,
    )
    
    logger.info(f"Tokens generated for Google user: {user_id}")
    return {"access_token": access_token, "refresh_token": refresh_token, "user": UserOut(id=user_id, name=name, email=email), "token_type": "bearer"}

# Refresh token endpoint
@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def refresh_token_endpoint(request: Request, response: Response):
    """
    Refresh access token using refresh token from httpOnly cookie.
    
    Args:
        request (Request): FastAPI request object to access cookies
        response (Response): FastAPI response object for setting new cookies
        
    Returns:
        TokenResponse: New JWT access token, refresh token, and user information
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    logger.info("Refresh token request received")
    
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning("Refresh token not found in cookies")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")
    
    try:
        payload = decode_token(refresh_token)
        # Verify this is a refresh token
        if payload.get("type") != "refresh":
            logger.warning("Invalid token type in refresh request")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Invalid token - missing user ID")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
        # Get user from database
        db = events.db
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            logger.warning(f"User not found for refresh token: {user_id}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        logger.info(f"Valid refresh token for user: {user_id}")
        
        # Create new tokens
        new_access_token = create_access_token(user_id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        new_refresh_token = create_refresh_token(user_id)
        
        # Set new refresh token in httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            max_age=60*60*24*7,
            path="/",            # FIX: Cookie available to all paths
            samesite="lax",
        )
        
        user_out = UserOut(id=user_id, name=user_doc.get("name"), email=user_doc.get("email"))
        logger.info(f"New tokens generated for user: {user_id}")
        return {"access_token": new_access_token, "refresh_token": new_refresh_token, "user": user_out, "token_type": "bearer"}
        
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

# Logout endpoint
@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing refresh token cookie.
    
    Args:
        response (Response): FastAPI response object for clearing cookies
        
    Returns:
        dict: Success message
    """
    logger.info("Logout request received")
    
    if settings.FRONTEND_URL.startswith("https://"):
        samesite_val = "none"
        secure_cookie = True
    elif "localhost" in settings.FRONTEND_URL:
        samesite_val = "lax"
        secure_cookie = False
    else:
        samesite_val = "none"
        secure_cookie = True

    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        max_age=0,
        path="/",            # FIX: Cookie available to all paths
        samesite=samesite_val,
        secure=secure_cookie,
    )
    
    logger.info("User logged out successfully")
    return {"message": "Logged out successfully"}

# Forgot password
@router.post("/forgot")
@limiter.limit(PASSWORD_RESET_RATE_LIMIT)
async def forgot_pass(request: Request, payload: ForgotPasswordIn):
    """
    Initiate password reset process by sending reset email.
    
    Args:
        payload (ForgotPasswordIn): Contains the user's email address
        
    Returns:
        dict: Success message (always returns success to prevent user enumeration)
    """
    logger.info(f"Password reset request for email: {payload.email}")
    
    db = events.db
    user = await db.users.find_one({"email": payload.email})
    if not user:
        logger.info(f"Password reset requested for non-existent email: {payload.email} (user enumeration prevention)")
        # avoid user enumeration
        return {"message": "If an account exists, an email was sent"}
    
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    
    try:
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"resetPasswordToken": token, "resetPasswordExpires": expires}})
        logger.info(f"Password reset token set for user: {str(user['_id'])}")
    except Exception as e:
        logger.error(f"Failed to set password reset token for user {str(user['_id'])}: {str(e)}")
        return {"message": "If an account exists, an email was sent"}
    
    reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}&email={payload.email}"
    
    try:
        await send_reset_email(payload.email, reset_url)
        logger.info(f"Password reset email sent to: {payload.email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {payload.email}: {str(e)}")
    
    return {"message": "If an account exists, an email was sent"}

# Reset password
@router.post("/reset")
@limiter.limit(PASSWORD_RESET_RATE_LIMIT)
async def reset_pass(request: Request, payload: ResetPasswordIn):
    """
    Reset user password using reset token.
    
    Args:
        payload (ResetPasswordIn): Contains the reset token and new password
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    logger.info("Password reset attempt with token")
    
    db = events.db
    user = await db.users.find_one({"resetPasswordToken": payload.token, "resetPasswordExpires": {"$gt": datetime.utcnow()}})
    if not user:
        logger.warning("Invalid or expired password reset token")
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    new_hash = hash_password(payload.new_password)
    
    try:
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"passwordHash": new_hash}, "$unset": {"resetPasswordToken": "", "resetPasswordExpires": ""}})
        logger.info(f"Password successfully reset for user: {str(user['_id'])}")
    except Exception as e:
        logger.error(f"Failed to reset password for user {str(user['_id'])}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")
    
    return {"message": "Password updated"}

# Get current user
@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user_flexible)):
    """
    Get current authenticated user information.
    
    Supports authentication via:
    1. Bearer token in Authorization header
    2. Refresh token in HTTP-only cookie

    Args:
        current_user: The authenticated user (injected by dependency)

    Returns:
        UserOut: Current user information

    Raises:
        HTTPException: If user is not authenticated
    """
    logger.info(f"Get /me request for user: {current_user.id}")
    
    # Log user activity
    await log_user_activity(current_user.id, "view_profile")
    
    user_out = UserOut(id=current_user.id, name=current_user.name, email=current_user.email)
    return user_out

