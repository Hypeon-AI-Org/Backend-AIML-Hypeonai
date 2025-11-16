import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    """Application configuration settings loaded from environment variables."""
    
    # Database settings
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    MONGO_DB: str = os.getenv("MONGO_DB", "hypeon_mvp_db")
    
    # Database connection pool settings
    MONGO_MAX_POOL_SIZE: int = int(os.getenv("MONGO_MAX_POOL_SIZE", "100"))
    MONGO_MIN_POOL_SIZE: int = int(os.getenv("MONGO_MIN_POOL_SIZE", "10"))
    MONGO_MAX_IDLE_TIME_MS: int = int(os.getenv("MONGO_MAX_IDLE_TIME_MS", "30000"))
    
    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "replace_me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Frontend settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS allowed origins
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "https://hypeon-dynamic-frontend.vercel.app",
        "https://app.hypeon.ai",
        "https://hypeon.ai"
    ]
    
    # Email settings
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASS: Optional[str] = os.getenv("SMTP_PASS")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM")
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    
    # Email Whitelist settings
    ENABLE_EMAIL_WHITELIST: bool = os.getenv("ENABLE_EMAIL_WHITELIST", "false").lower() == "true"
    WHITELISTED_EMAILS: list = [
        email.strip().lower() 
        for email in os.getenv("WHITELISTED_EMAILS", "").split(",") 
        if email.strip()
    ]

# Global settings instance
settings = Settings()