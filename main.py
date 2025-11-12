import os
from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from datetime import datetime

from app.routes import auth, products, saved_searches
from app.core import events
from app.core.config import settings
from app.utils.rate_limiter import limiter, rate_limit_exceeded_handler
from app.utils.logger import logger

# Global database client - initialized in startup event
client: AsyncIOMotorClient = None

# Security headers middleware
async def add_security_headers(request: Request, call_next):
    """Middleware to add comprehensive security headers to all responses."""
    try:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https:;"
        return response
    except Exception as e:
        logger.error(f"Security headers middleware error: {str(e)}")
        response = Response("Internal server error", status_code=500)
        return response

# Initialize the FastAPI application with a descriptive title
app = FastAPI(title="Hypeon Backend (FastAPI)")

# Add security headers middleware
app.middleware("http")(add_security_headers)

# Configure CORS origins based on environment
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production frontend URL if available
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    cors_origins.append(frontend_url)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Access-Control-Allow-Origin"],
    max_age=3600
)

# Add rate limiter to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Include API routers with appropriate prefixes and tags for documentation
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(saved_searches.router, prefix="/api/saved-searches", tags=["saved-searches"])

# Register startup and shutdown event handlers for database connection management
app.add_event_handler("startup", events.startup)
app.add_event_handler("shutdown", events.shutdown)

@app.get("/")
def root():
    return {"status": "Hypeon AI backend running successfully 🚀"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    """Basic health check endpoint that returns the status of the application."""
    return {"status": "healthy", "service": "Hypeon AI Backend"}

@app.get("/health/db")
async def health_db():
    """Test database connectivity."""
    try:
        if client is None:
            return {"status": "error", "message": "Database client not initialized"}
        
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "database": settings.MONGO_DB,
            "message": "MongoDB connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }, 503


@app.get("/health/full")
async def health_full():
    """Comprehensive health check including database."""
    try:
        db_status = "healthy"
        db_message = "Connected"
        
        if client is None:
            db_status = "unhealthy"
            db_message = "Client not initialized"
        else:
            try:
                await client.admin.command('ping')
            except Exception as e:
                db_status = "unhealthy"
                db_message = str(e)
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "status": db_status,
                "message": db_message,
                "database_name": settings.MONGO_DB
            },
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Full health check failed: {str(e)}")
        return {"status": "unhealthy", "message": str(e)}, 503

# Add after app initialization
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status": 500,
            "message": str(exc) if os.getenv("ENVIRONMENT") != "production" else "An error occurred"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler for structured error responses."""
    logger.warning(f"HTTP Exception - Status: {exc.status_code}, Detail: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status": exc.status_code
        }
    )