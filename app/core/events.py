from __future__ import annotations

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.utils.logger import logger

# Global database client and database instances
# These are initialized during startup and cleaned up during shutdown
client = None
db = None

async def startup():
    """
    Application startup event handler.
    
    Initializes the MongoDB connection with proper connection pooling and creates required indexes.
    This function is called automatically when the FastAPI application starts.
    """
    global client, db
    try:
        # Initialize MongoDB client with connection pooling settings
        client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
            minPoolSize=settings.MONGO_MIN_POOL_SIZE,
            maxIdleTimeMS=settings.MONGO_MAX_IDLE_TIME_MS,
            serverSelectionTimeoutMS=5000,  # Timeout for server selection (5 seconds)
            connectTimeoutMS=5000,  # Timeout for initial connection (5 seconds)
            socketTimeoutMS=5000,   # Timeout for socket operations (5 seconds)
        )
        db = client[settings.MONGO_DB]
        
        # Test database connection
        await client.admin.command('ping')
        logger.info("✅ MongoDB connection established successfully")
        
        # Create indexes
        await db.users.create_index("email", unique=True)
        await db.products.create_index([("title", "text")])
        await db.products.create_index([("niche", 1), ("platform", 1), ("region", 1), ("hypeScore", -1)])
        await db.saved_searches.create_index([("userId", 1), ("createdAt", -1)])
        
        # Create indexes for user activity tracking
        await db.user_activity.create_index([("userId", 1), ("timestamp", -1)])
        await db.user_activity.create_index("action")
        
        logger.info("✅ MongoDB connected and indexes created")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MongoDB connection: {str(e)}")
        raise

async def shutdown():
    """
    Application shutdown event handler.
    
    Closes the MongoDB connection gracefully.
    This function is called automatically when the FastAPI application shuts down.
    """
    global client
    if client:
        try:
            client.close()
            logger.info("✅ MongoDB connection closed gracefully")
        except Exception as e:
            logger.error(f"❌ Error closing MongoDB connection: {str(e)}")