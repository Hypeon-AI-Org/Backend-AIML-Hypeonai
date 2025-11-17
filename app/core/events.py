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
    
    # Validate MONGO_URI is set
    if not settings.MONGO_URI:
        logger.error("❌ MONGO_URI is not set in environment variables")
        raise ValueError("MONGO_URI environment variable is required")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔗 Attempting MongoDB connection (attempt {attempt + 1}/{max_retries})...")
            logger.debug(f"Connecting to: {settings.MONGO_URI.split('@')[1] if '@' in settings.MONGO_URI else 'MongoDB'}")
            
            # Initialize MongoDB client with connection pooling settings
            # Increased timeouts for Atlas connections which may take longer
            # Note: mongodb+srv:// automatically enables TLS, so we don't set it explicitly
            client = AsyncIOMotorClient(
                settings.MONGO_URI,
                maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
                minPoolSize=settings.MONGO_MIN_POOL_SIZE,
                maxIdleTimeMS=settings.MONGO_MAX_IDLE_TIME_MS,
                serverSelectionTimeoutMS=30000,  # Increased to 30 seconds for Atlas
                connectTimeoutMS=30000,  # Increased to 30 seconds for initial connection
                socketTimeoutMS=30000,   # Increased to 30 seconds for socket operations
                retryWrites=True,
                w="majority",
                # Additional options for better Atlas compatibility
                heartbeatFrequencyMS=10000,  # Check server status every 10 seconds
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
            error_msg = str(e)
            logger.warning(f"⚠️ MongoDB connection attempt {attempt + 1} failed: {error_msg}")
            
            # Provide helpful error messages
            if "authentication failed" in error_msg.lower():
                logger.error("💡 Tip: Check your MongoDB username and password in MONGO_URI")
            elif "timeout" in error_msg.lower() or "no replica set members" in error_msg.lower():
                logger.error("💡 Tip: Check your network connection and MongoDB Atlas IP whitelist")
                logger.error("💡 Tip: Ensure your IP address is whitelisted in MongoDB Atlas Network Access")
            elif "tls" in error_msg.lower() or "ssl" in error_msg.lower():
                logger.error("💡 Tip: Check TLS/SSL configuration in your connection string")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"❌ MongoDB initialization failed after {max_retries} attempts")
                logger.error("💡 Common solutions:")
                logger.error("   1. Verify MONGO_URI in .env file is correct")
                logger.error("   2. Check MongoDB Atlas IP whitelist includes your IP")
                logger.error("   3. Verify database user credentials are correct")
                logger.error("   4. Ensure connection string includes ?retryWrites=true&w=majority")
                raise


async def _create_indexes(database):
    """
    Create database indexes with error handling.
    Logs each index creation attempt for debugging.
    """
    indexes = [
        ("users", [("email", 1)], {"unique": True}, "email unique index"),
        ("products", [("title", "text")], {}, "products full-text index"),
        # Updated to use actual database field names
        ("products", [("niche", 1), ("Product Type", 1), ("region", 1), ("Hype Score", -1)], {}, "products compound index"),
        # Add indexes for commonly filtered fields
        ("products", [("Category", 1)], {}, "products category index"),
        ("products", [("color", 1)], {}, "products color index"),
        ("products", [("Sales", 1)], {}, "products sales index"),
        # Performance: Add indexes for sorting (most common sort field)
        ("products", [("Hype Score", -1)], {}, "products hype score sort index"),
        # Performance: Compound indexes for common filter + sort combinations
        ("products", [("niche", 1), ("Hype Score", -1)], {}, "products niche + score index"),
        ("products", [("region", 1), ("Hype Score", -1)], {}, "products region + score index"),
        ("products", [("Category", 1), ("Hype Score", -1)], {}, "products category + score index"),
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