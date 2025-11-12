from app.schemas import UserActivity
from app.core import events
from app.utils.logger import logger
from datetime import datetime
from typing import Optional, Dict, Any

async def log_user_activity(user_id: str, action: str, params: Optional[Dict[str, Any]] = None):
    """
    Log user activity to the database.
    
    Args:
        user_id (str): The ID of the user performing the action
        action (str): The action being performed (e.g., "search", "view_product")
        params (dict, optional): Additional parameters related to the action
    """
    try:
        # Create activity record
        activity = UserActivity(
            userId=user_id,
            action=action,
            params=params
        )
        
        # Insert into database
        db = events.db
        result = await db.user_activity.insert_one(activity.dict())
        logger.info(f"User activity logged - ID: {result.inserted_id}, User: {user_id}, Action: {action}")
        
    except Exception as e:
        logger.error(f"Failed to log user activity for user {user_id}, action {action}: {str(e)}")