import os
from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routes import auth, products, saved_searches
from app.core import events
from app.utils.rate_limiter import limiter, rate_limit_exceeded_handler

# Security headers middleware
async def add_security_headers(request: Request, call_next):
    """Middleware to add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
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
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Access-Control-Allow-Origin"]
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
async def root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Hypeon AI Backend (FastAPI) ✅"}

@app.get("/health")
async def health_check():
    """Basic health check endpoint that returns the status of the application."""
    return {"status": "healthy", "service": "Hypeon AI Backend"}

@app.get("/health/db")
async def database_health_check():
    """Database health check endpoint that verifies database connectivity and provides detailed info."""
    try:
        # Check if the database connection is alive
        db = events.db
        if db is not None:
            # Run a simple ping command to test the connection
            await db.command('ping')
            
            # Get database stats
            db_stats = await db.command('dbStats')
            
            return {
                "status": "healthy", 
                "database": "connected",
                "collections": db_stats.get("collections", 0),
                "objects": db_stats.get("objects", 0),
                "avgObjSize": db_stats.get("avgObjSize", 0),
                "dataSize": db_stats.get("dataSize", 0)
            }
        else:
            return {"status": "unhealthy", "database": "not connected", "details": "Database instance is None"}
    except Exception as e:
        return {"status": "unhealthy", "database": "connection error", "details": str(e)}

@app.get("/health/full")
async def full_health_check():
    """Comprehensive health check endpoint that verifies all system dependencies."""
    health_status = {
        "status": "healthy",
        "service": "Hypeon AI Backend",
        "checks": {}
    }
    
    # Check database
    try:
        db = events.db
        if db is not None:
            await db.command('ping')
            health_status["checks"]["database"] = {"status": "healthy", "details": "Connected"}
        else:
            health_status["checks"]["database"] = {"status": "unhealthy", "details": "Not connected"}
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "details": str(e)}
        health_status["status"] = "unhealthy"
    
    # Check environment variables
    required_env_vars = ["MONGO_URI", "JWT_SECRET"]
    missing_env_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_env_vars.append(var)
    
    if missing_env_vars:
        health_status["checks"]["environment"] = {
            "status": "degraded", 
            "details": f"Missing environment variables: {', '.join(missing_env_vars)}"
        }
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    else:
        health_status["checks"]["environment"] = {"status": "healthy", "details": "All required variables present"}
    
    return health_status