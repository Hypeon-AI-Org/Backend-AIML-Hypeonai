from __future__ import annotations

import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.utils.logger import logger

# Global database client and database instances
# These are initialized during startup and cleaned up during shutdown
client: Optional[AsyncIOMotorClient] = None
db = None

async def startup():
    """
    Application startup event handler.
    
    Initializes the MongoDB connection with proper connection pooling and creates required indexes.
    Implements retry logic for connection failures.
    This function is called automatically when the FastAPI application starts.
    """
    global client, db
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔗 Attempting MongoDB connection (attempt {attempt + 1}/{max_retries})...")
            
            # Initialize MongoDB client with connection pooling settings
            client = AsyncIOMotorClient(
                settings.MONGO_URI,
                maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
                minPoolSize=settings.MONGO_MIN_POOL_SIZE,
                maxIdleTimeMS=settings.MONGO_MAX_IDLE_TIME_MS,
                serverSelectionTimeoutMS=5000,  # Timeout for server selection (5 seconds)
                connectTimeoutMS=5000,  # Timeout for initial connection (5 seconds)
                socketTimeoutMS=5000,   # Timeout for socket operations (5 seconds)
                retryWrites=True,
                w="majority",
            )
            db = client[settings.MONGO_DB]
            
            # Test database connection with ping
            await client.admin.command('ping')
            logger.info(f"✅ MongoDB connection established to {settings.MONGO_DB}")
            
            # Create indexes with error handling
            await _create_indexes(db)
            logger.info("✅ Database indexes created successfully")
            return
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"❌ MongoDB initialization failed after {max_retries} attempts")
                raise


async def _create_indexes(database):
    """
    Create database indexes with error handling.
    Logs each index creation attempt for debugging.
    """
    indexes = [
        ("users", [("email", 1)], {"unique": True}, "email unique index"),
        ("products", [("title", "text")], {}, "products full-text index"),
        ("products", [("niche", 1), ("platform", 1), ("region", 1), ("hypeScore", -1)], {}, "products compound index"),
        ("saved_searches", [("userId", 1), ("createdAt", -1)], {}, "saved_searches compound index"),
        ("user_activity", [("userId", 1), ("timestamp", -1)], {}, "user_activity compound index"),
        ("user_activity", [("action", 1)], {}, "user_activity action index"),
    ]
    
    for collection_name, keys, options, description in indexes:
        try:
            collection = database[collection_name]
            await collection.create_index(keys, **options)
            logger.debug(f"✓ Created {description}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create {description}: {str(e)}")


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


async def get_db():
    """
    Dependency function to provide database instance to routes.
    """
    if db is None:
        raise RuntimeError("Database not initialized. Ensure startup() was called.")
    return db