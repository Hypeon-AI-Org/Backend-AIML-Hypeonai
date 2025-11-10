"""MongoDB connection module for Hypeon AI Backend."""

import os
import logging
from pymongo import MongoClient
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MongoClient instance
_client: Optional[MongoClient] = None
_db = None


def get_mongo_client() -> MongoClient:
    """
    Get or create a global MongoClient instance.
    
    Returns:
        MongoClient instance
    """
    global _client
    
    if _client is None:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI environment variable is not set")
        
        _client = MongoClient(mongo_uri)
        logger.info("MongoDB client initialized successfully")
    
    return _client


def get_collection(collection_name: str):
    """
    Get a collection from the hypeon_processed database.
    
    Args:
        collection_name: Name of the collection to retrieve
        
    Returns:
        Collection object from MongoDB
    """
    global _db
    
    if _db is None:
        client = get_mongo_client()
        _db = client["hypeon_processed"]
        logger.info("Connected to database: hypeon_processed")
    
    return _db[collection_name]

