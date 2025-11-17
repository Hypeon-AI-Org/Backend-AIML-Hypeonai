from fastapi import APIRouter, Depends, Query, Request, HTTPException
from typing import Optional
from app.core import events
from app.utils.logger import logger
from app.utils.activity_tracker import log_user_activity
from app.deps import get_current_user
from bson import ObjectId
import re

# Create router instance for product-related endpoints
router = APIRouter()

# Field name mapping from API format to database format
FIELD_MAPPING = {
    "hypeScore": "Hype Score",
    "weeklyGrowth": "Weekly Growth",
    "monthlyGrowth": "Monthly growth",
    "productName": "Product Name",
    "productType": "Product Type",
    "category": "Category",
    "color": "color",
    "gid": "g:id",
    "gImageLink": "g:image_link",
    "gAdditionalImageLink": "g:additional_image_link",
    "sales": "Sales",
    "title": "title",  # Already matches
    "niche": "niche",  # Already matches
    "region": "region",  # Already matches
}

@router.get("/")
async def list_products(request: Request, 
                        niche: Optional[str] = Query(None), 
                        platform: Optional[str] = Query(None), 
                        region: Optional[str] = Query(None),
                        category: Optional[str] = Query(None),
                        color: Optional[str] = Query(None),
                        sales: Optional[str] = Query(None),
                        limit: int = Query(50, ge=1, le=1000, description="Number of results to return (1-1000)"), 
                        offset: int = Query(0, ge=0, description="Number of results to skip"), 
                        sort: str = Query("Hype Score:desc", description="Sort field and direction (format: 'field:asc' or 'field:desc')"), 
                        q: Optional[str] = Query(None, description="Text search query"),
                        include_total: bool = Query(False, description="Include total count (slower, use only when needed for pagination UI)"),
                        current_user=Depends(get_current_user)):
    """
    List products with optional filtering and sorting.
    
    Args:
        request (Request): FastAPI request object
        niche (str, optional): Filter by product niche
        platform (str, optional): Filter by platform - maps to 'Product Type'
        region (str, optional): Filter by region
        category (str, optional): Filter by category
        color (str, optional): Filter by color
        sales (str, optional): Filter by sales level (e.g., 'HIGH', 'MEDIUM', 'LOW')
        limit (int): Maximum number of products to return (default: 50)
        offset (int): Number of products to skip (default: 0)
        sort (str): Sort field and direction in format "field:direction" (default: "Hype Score:desc")
                   Accepts both API format (hypeScore) and DB format (Hype Score)
        q (str, optional): Text search query
        include_total (bool): Include total count in response (default: False, set to True only when needed for pagination UI)
        current_user: The authenticated user (injected by dependency)
        
    Returns:
        dict: Contains total count (if include_total=True), pagination info, and list of products
    """
    logger.info(f"Product list request - niche: {niche}, platform: {platform}, region: {region}, category: {category}, color: {color}, sales: {sales}, query: {q}")
    
    # Log user activity with error handling
    try:
        search_params = {}
        if niche:
            search_params["niche"] = niche
        if platform:
            search_params["platform"] = platform
        if region:
            search_params["region"] = region
        if category:
            search_params["category"] = category
        if color:
            search_params["color"] = color
        if sales:
            search_params["sales"] = sales
        if q:
            search_params["query"] = q
        
        await log_user_activity(current_user.id, "search", search_params)
    except Exception as e:
        logger.warning(f"Failed to log user activity: {str(e)}")
        # Continue execution even if logging fails
    
    db = events.db
    query = {}
    if niche:
        query["niche"] = niche
    if platform:
        # Map platform to Product Type if needed, or use as-is if it's already the correct field
        query["Product Type"] = platform
    if region:
        query["region"] = region
    if category:
        query["Category"] = category
    if color:
        query["color"] = color
    if sales:
        query["Sales"] = sales
    if q:
        # Use text search on title or Product Name
        query["$text"] = {"$search": q}
    
    # Validate and parse sort parameter
    # Format should be "field:asc" or "field:desc"
    sort_pattern = r"^[\w\s]+:(asc|desc)$"
    if not re.match(sort_pattern, sort):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid sort format. Expected 'field:asc' or 'field:desc', got '{sort}'"
        )
    
    # Parse sort and map field name
    field, order = sort.split(":")
    # Map API field name to database field name if mapping exists
    db_field = FIELD_MAPPING.get(field, field)
    
    # Validate sort direction
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort direction. Expected 'asc' or 'desc', got '{order}'"
        )
    
    sort_dir = -1 if order == "desc" else 1
    
    # Count documents only if requested (this is slow on large collections)
    total = None
    if include_total:
        try:
            total = await db.products.count_documents(query)
            logger.info(f"Found {total} products matching criteria")
        except Exception as e:
            logger.warning(f"Error counting products: {str(e)}")
            # Don't fail the request if count fails, just set total to None
            total = None
    
    try:
        # Use the mapped database field name for sorting
        cursor = db.products.find(query).sort(db_field, sort_dir).skip(offset).limit(limit)
        
        # Use to_list() instead of async for - much faster for small result sets
        # This fetches all documents in one batch operation
        docs = await cursor.to_list(length=limit)
        
        # Process documents efficiently
        items = []
        for doc in docs:
            if doc:
                # Convert ObjectId to string and preserve all other fields
                # MongoDB documents are already dict-like, so we can modify in place
                doc["id"] = str(doc.pop("_id"))
                
                # Map "Product Name" to "title" for frontend compatibility
                if "Product Name" in doc and doc["Product Name"]:
                    doc["title"] = doc["Product Name"]
                elif "title" not in doc:
                    doc["title"] = ""
                
                items.append(doc)
        
        logger.info(f"Retrieved {len(items)} products (limit: {limit}, offset: {offset})")
    except Exception as e:
        logger.error(f"Error retrieving products: {str(e)}")
        # Log the field name being used for debugging
        logger.error(f"Sort field attempted: {db_field}, Original field: {field}")
        raise
    
    return {"total": total, "limit": limit, "offset": offset, "returned": len(items), "items": items}

@router.get("/{product_id}")
async def get_product(product_id: str, current_user=Depends(get_current_user)):
    """
    Get a specific product by its ID.
    
    Args:
        product_id (str): The MongoDB ObjectId of the product
        current_user: The authenticated user (injected by dependency)
        
    Returns:
        dict: The product data or error message
    """
    logger.info(f"Product detail request for ID: {product_id}")
    
    # Validate ObjectId format before attempting database query
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid product ID format: '{product_id}'. Expected a valid MongoDB ObjectId."
        )
    
    # Log user activity with error handling
    try:
        await log_user_activity(current_user.id, "view_product", {"product_id": product_id})
    except Exception as e:
        logger.warning(f"Failed to log user activity: {str(e)}")
    
    db = events.db
    try:
        doc = await db.products.find_one({"_id": ObjectId(product_id)})
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving product from database"
        )
    
    if not doc:
        logger.info(f"Product not found: {product_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID '{product_id}' not found"
        )
    
    try:
        # Optimize: MongoDB documents are already dict-like, modify in place
        doc["id"] = str(doc.pop("_id"))
        
        # Map "Product Name" to "title" for frontend compatibility
        if "Product Name" in doc and doc["Product Name"]:
            doc["title"] = doc["Product Name"]
        elif "title" not in doc:
            doc["title"] = ""
        
        logger.info(f"Product retrieved successfully: {product_id}")
        logger.debug(f"Product fields: {list(doc.keys())}")
        return doc
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Error processing product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing product data"
        )