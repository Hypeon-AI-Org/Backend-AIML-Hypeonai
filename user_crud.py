"""User CRUD operations for Hypeon AI Authentication System."""

from typing import Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from fastapi import HTTPException
import bcrypt
from database.mongo_connection import get_collection
from models import UserCreate, UserInDB, AuthProvider


def init_indexes():
    """Initialize database indexes for users collection."""
    users_collection = get_collection("users")
    users_collection.create_index("email", unique=True)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get a user by email."""
    users_collection = get_collection("users")
    user_doc = users_collection.find_one({"email": email})
    
    if user_doc:
        return UserInDB(
            id=str(user_doc["_id"]),
            name=user_doc["name"],
            email=user_doc["email"],
            picture=user_doc.get("picture"),
            auth_provider=user_doc["auth_provider"],
            google_id=user_doc.get("google_id"),
            password_hash=user_doc.get("password_hash"),
            created_at=user_doc["created_at"]
        )
    
    return None


async def get_user_by_google_id(google_id: str) -> Optional[UserInDB]:
    """Get a user by Google ID."""
    users_collection = get_collection("users")
    user_doc = users_collection.find_one({"google_id": google_id})
    
    if user_doc:
        return UserInDB(
            id=str(user_doc["_id"]),
            name=user_doc["name"],
            email=user_doc["email"],
            picture=user_doc.get("picture"),
            auth_provider=user_doc["auth_provider"],
            google_id=user_doc.get("google_id"),
            password_hash=user_doc.get("password_hash"),
            created_at=user_doc["created_at"]
        )
    
    return None


async def create_user(user_data: UserCreate, password: Optional[str] = None) -> UserInDB:
    """Create a new user."""
    users_collection = get_collection("users")
    
    # Hash password if provided (for local auth)
    password_hash = None
    if password:
        password_hash = hash_password(password)
    
    user_doc = {
        "name": user_data.name,
        "email": user_data.email,
        "picture": user_data.picture,
        "auth_provider": user_data.auth_provider.value,
        "google_id": user_data.google_id,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    }
    
    try:
        result = users_collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        return UserInDB(
            id=str(user_doc["_id"]),
            name=user_doc["name"],
            email=user_doc["email"],
            picture=user_doc.get("picture"),
            auth_provider=user_doc["auth_provider"],
            google_id=user_doc.get("google_id"),
            password_hash=user_doc.get("password_hash"),
            created_at=user_doc["created_at"]
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user with email and password."""
    user = await get_user_by_email(email)
    
    if not user or not user.password_hash:
        return None
    
    if verify_password(password, user.password_hash):
        return user
    
    return None