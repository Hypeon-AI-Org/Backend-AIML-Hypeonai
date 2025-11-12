from fastapi import APIRouter, Depends, HTTPException, status
from app.deps import get_current_user, get_db
from app.schemas import SavedSearchIn
from app.utils.logger import logger
from app.utils.activity_tracker import log_user_activity
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter()

def serialize_saved_search(doc):
    """Convert MongoDB document to JSON-safe format."""
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    doc["userId"] = str(doc["userId"])
    del doc["_id"]
    return doc

# List saved searches
@router.get("/", response_model=list)
async def list_saved_searches(current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    List all saved searches for the current user.
    
    Args:
        current_user: The authenticated user (injected by dependency)
        db: Database connection (injected by dependency)
        
    Returns:
        list: List of saved searches for the current user
    """
    logger.info(f"Listing saved searches for user: {current_user.id}")
    
    # Log user activity
    await log_user_activity(current_user.id, "list_saved_searches")
    
    docs = []
    try:
        cursor = db.saved_searches.find({"userId": ObjectId(current_user.id)}).sort("createdAt", -1)
        async for d in cursor:
            docs.append(serialize_saved_search(d))
        logger.info(f"Retrieved {len(docs)} saved searches for user: {current_user.id}")
    except Exception as e:
        logger.error(f"Error retrieving saved searches for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve saved searches")
    
    return docs

# Create new saved search
@router.post("/")
async def create_saved_search(payload: SavedSearchIn, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Create a new saved search for the current user.
    
    Args:
        payload (SavedSearchIn): The saved search data
        current_user: The authenticated user (injected by dependency)
        db: Database connection (injected by dependency)
        
    Returns:
        dict: The created saved search
    """
    logger.info(f"Creating saved search for user: {current_user.id}")
    
    # Log user activity
    await log_user_activity(current_user.id, "create_saved_search", {
        "name": payload.name,
        "params": payload.params
    })
    
    doc = {
        "userId": ObjectId(current_user.id),
        "name": payload.name,
        "params": payload.params,
        "createdAt": datetime.utcnow(),
        "resultSnapshot": payload.snapshot or [],
        "notes": payload.notes
    }
    
    try:
        res = await db.saved_searches.insert_one(doc)
        saved_doc = await db.saved_searches.find_one({"_id": res.inserted_id})
        logger.info(f"Saved search created with ID: {str(res.inserted_id)} for user: {current_user.id}")
    except Exception as e:
        logger.error(f"Error creating saved search for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create saved search")
    
    return serialize_saved_search(saved_doc)

# Get one
@router.get("/{id}")
async def get_saved_search(id: str, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Get a specific saved search by ID.
    
    Args:
        id (str): The saved search ID
        current_user: The authenticated user (injected by dependency)
        db: Database connection (injected by dependency)
        
    Returns:
        dict: The requested saved search
        
    Raises:
        HTTPException: If the saved search is not found or doesn't belong to the user
    """
    logger.info(f"Retrieving saved search {id} for user: {current_user.id}")
    
    # Log user activity
    await log_user_activity(current_user.id, "view_saved_search", {"search_id": id})
    
    try:
        oid = ObjectId(id)
    except InvalidId:
        logger.warning(f"Invalid ID format for saved search: {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid ID format")
    
    try:
        doc = await db.saved_searches.find_one({"_id": oid})
    except Exception as e:
        logger.error(f"Error retrieving saved search {id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve saved search")
    
    if not doc:
        logger.info(f"Saved search not found: {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found")
    
    if str(doc["userId"]) != current_user.id:
        logger.warning(f"User {current_user.id} attempted to access saved search {id} belonging to another user")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this saved search")
    
    logger.info(f"Saved search {id} retrieved successfully for user: {current_user.id}")
    return serialize_saved_search(doc)

# Delete
@router.delete("/{id}")
async def delete_saved_search(id: str, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Delete a specific saved search by ID.
    
    Args:
        id (str): The saved search ID
        current_user: The authenticated user (injected by dependency)
        db: Database connection (injected by dependency)
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If the saved search is not found or doesn't belong to the user
    """
    logger.info(f"Deleting saved search {id} for user: {current_user.id}")
    
    # Log user activity
    await log_user_activity(current_user.id, "delete_saved_search", {"search_id": id})
    
    try:
        oid = ObjectId(id)
    except InvalidId:
        logger.warning(f"Invalid ID format for saved search: {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid ID format")
    
    try:
        doc = await db.saved_searches.find_one({"_id": oid})
    except Exception as e:
        logger.error(f"Error retrieving saved search {id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve saved search")
    
    if not doc:
        logger.info(f"Saved search not found: {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found")
    
    if str(doc["userId"]) != current_user.id:
        logger.warning(f"User {current_user.id} attempted to delete saved search {id} belonging to another user")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this saved search")
    
    try:
        await db.saved_searches.delete_one({"_id": oid})
        logger.info(f"Saved search {id} deleted successfully for user: {current_user.id}")
    except Exception as e:
        logger.error(f"Error deleting saved search {id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete saved search")
    
    return {"message": "Deleted"}