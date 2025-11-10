"""Database connection module for Hypeon AI Backend."""

from .mongo_connection import get_collection, get_mongo_client

__all__ = ['get_collection', 'get_mongo_client']

