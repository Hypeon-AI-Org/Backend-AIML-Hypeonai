from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.core import events
from app.utils.logger import logger
from app.utils.activity_tracker import log_user_activity
from app.deps import get_current_user
from bson import ObjectId

# Create router instance for product-related endpoints
router = APIRouter()

@router.get("/")
async def list_products(request: Request, niche: Optional[str] = Query(None), platform: Optional[str] = Query(None), region: Optional[str] = Query(None),
                        limit: int = 50, offset: int = 0, sort: str = "hypeScore:desc", q: Optional[str] = None,
                        current_user=Depends(get_current_user)):
    """
    List products with optional filtering and sorting.
    
    Args:
        request (Request): FastAPI request object
        niche (str, optional): Filter by product niche
        platform (str, optional): Filter by platform (e.g., 'amazon', 'shopify')
        region (str, optional): Filter by region
        limit (int): Maximum number of products to return (default: 50)
        offset (int): Number of products to skip (default: 0)
        sort (str): Sort field and direction in format "field:direction" (default: "hypeScore:desc")
        q (str, optional): Text search query
        current_user: The authenticated user (injected by dependency)
        
    Returns:
        dict: Contains total count, pagination info, and list of products
    """
    logger.info(f"Product list request - niche: {niche}, platform: {platform}, region: {region}, query: {q}")
    
    # Log user activity
    search_params = {}
    if niche:
        search_params["niche"] = niche
    if platform:
        search_params["platform"] = platform
    if region:
        search_params["region"] = region
    if q:
        search_params["query"] = q
    
    await log_user_activity(current_user.id, "search", search_params)
    
    db = events.db
    query = {}
    if niche:
        query["niche"] = niche
    if platform:
        query["platform"] = platform
    if region:
        query["region"] = region
    if q:
        query["$text"] = {"$search": q}
    
    # parse sort
    field, order = (sort.split(":")[0], sort.split(":")[1]) if ":" in sort else (sort, "desc")
    sort_dir = -1 if order == "desc" else 1
    
    try:
        total = await db.products.count_documents(query)
        logger.info(f"Found {total} products matching criteria")
    except Exception as e:
        logger.error(f"Error counting products: {str(e)}")
        raise
    
    try:
        cursor = db.products.find(query).sort(field, sort_dir).skip(offset).limit(limit)
        items = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            items.append(doc)
        logger.info(f"Retrieved {len(items)} products (limit: {limit}, offset: {offset})")
    except Exception as e:
        logger.error(f"Error retrieving products: {str(e)}")
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
    
    # Log user activity
    await log_user_activity(current_user.id, "view_product", {"product_id": product_id})
    
    db = events.db
    try:
        doc = await db.products.find_one({"_id": ObjectId(product_id)})
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        return {"message": "Error retrieving product"}, 500
    
    if not doc:
        logger.info(f"Product not found: {product_id}")
        return {"message": "Not found"}, 404
    
    try:
        doc["id"] = str(doc["_id"])
        del doc["_id"] 
        logger.info(f"Product retrieved successfully: {product_id}")
    except Exception as e:
        logger.error(f"Error processing product {product_id}: {str(e)}")
        return {"message": "Error processing product"}, 500
    
    return doc