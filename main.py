"""Main FastAPI application for Hypeon AI Metrics."""

# Load environment variables from .env file first
from dotenv import load_dotenv
load_dotenv()

# Initialize database indexes
from user_crud import init_indexes
init_indexes()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any, Literal
import pandas as pd
import logging
from datetime import datetime

from config import settings
from data_loader import load_all_data
from metrics.growth_rate import (
    calculate_growth_rate,
    calculate_product_level_shopify_growth,
    calculate_product_level_amazon_growth
)
from metrics.sentiment_score import calculate_sentiment_score
from metrics.trend_index import calculate_trend_index
from metrics.engagement import engagement as calculate_engagement
from metrics.hype import calculate_hype_score
from auth_router import router as auth_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data store
dataframes: Dict[str, pd.DataFrame] = {}

# Include authentication router
app.include_router(auth_router)


@app.on_event("startup")
async def load_data():
    """Load all data at application startup."""
    global dataframes
    try:
        logger.info(f"Loading data from {settings.DATA_BASE_PATH}...")
        # Load real data (use sample_size=None for production, or set a limit for dev)
        dataframes = load_all_data(sample_size=settings.DATA_SAMPLE_SIZE)
        
        if not dataframes:
            logger.warning("No dataframes loaded!")
        else:
            logger.info(f"Successfully loaded {len(dataframes)} dataframes:")
            for name, df in dataframes.items():
                logger.info(f"  - {name}: {len(df)} rows, columns: {list(df.columns)}")
    except Exception as e:
        logger.error(f"Error loading data: {e}", exc_info=True)
        raise


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Hypeon AI Analytics API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/metrics/growth",
            "/metrics/combined",
            "/health"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    data_info = {}
    for name, df in dataframes.items():
        data_info[name] = {
            "rows": len(df),
            "columns": len(df.columns)
        }
    
    return {
        "status": "healthy",
        "data_loaded": len(dataframes) > 0,
        "dataframe_count": len(dataframes),
        "data_info": data_info
    }


@app.get("/metrics/growth")
async def get_growth_rate(
    niche: Optional[str] = Query(None, description="Filter by product niche (required for product-level)"),
    level: Literal['niche', 'product'] = Query('niche', description="Aggregation level: 'niche' or 'product'"),
    source: Literal['shopify', 'amazon', 'all'] = Query('all', description="Data source: 'shopify', 'amazon', or 'all' (only for product-level)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination")
):
    """
    Calculate and return growth rate metrics at niche or product level.
    
    **Niche-level (default)**:
    - Combines Shopify (25%), Amazon (35%), TikTok (30%), Reddit (10%)
    - Returns aggregated growth rate per niche
    
    **Product-level**:
    - Requires `niche` parameter
    - Returns individual products with commerce_score and social_enrichment
    - Formula: growth_rate = 0.8 * commerce_score + 0.2 * social_enrichment
    - `source=shopify`: Shopify products only
    - `source=amazon`: Amazon products only
    - `source=all`: Both platforms (separate arrays)
    
    Args:
        niche: Optional filter by niche (case-insensitive, required for product-level)
        level: Aggregation level ('niche' or 'product')
        source: Data source filter ('shopify', 'amazon', or 'all')
        
    Returns:
        Niche-level: {"total_count": n, "data": [{"niche": "...", "growth_rate": 0.66}, ...]}
        Product-level: {"total_count": m, "source": "shopify", "niche": "...", "data": [...]}
    """
    if not dataframes:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        # Niche-level calculation (default, unchanged)
        if level == 'niche':
            logger.info(f"Calculating niche-level growth rates (niche filter: {niche})...")
            growth_df = calculate_growth_rate(dataframes)
            
            if growth_df.empty:
                return {
                    "total_count": 0,
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "data": []
                }
            
            # Filter by niche if provided
            if niche:
                growth_df = growth_df[growth_df['niche'].str.lower() == niche.lower()]  # type: ignore[reportAttributeAccessIssue]
            
            # Apply pagination
            total_count = len(growth_df)
            # Ensure growth_df is a DataFrame before using iloc
            if isinstance(growth_df, pd.DataFrame):
                growth_df = growth_df.iloc[offset:offset + limit]
            else:
                growth_df = pd.DataFrame()
            
            # Convert to records
            result = growth_df.fillna("").to_dict(orient='records')  # type: ignore
            
            return {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "returned_count": len(result),
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "data": result
            }
        
        # Product-level calculation (new)
        else:
            if not niche:
                raise HTTPException(
                    status_code=400,
                    detail="Niche parameter is required for product-level growth rate"
                )
            
            logger.info(f"Calculating product-level growth rates (niche: {niche}, source: {source})...")
            
            # Calculate for specific source
            if source == 'shopify':
                product_df = calculate_product_level_shopify_growth(dataframes, niche)
                
                if product_df.empty:
                    return {
                        "total_count": 0,
                        "source": "shopify",
                        "niche": niche,
                        "last_updated": datetime.utcnow().isoformat() + "Z",
                        "data": []
                    }
                
                # Add niche to each record and reorder columns
                product_df['niche'] = niche
                # Reorder: product_id, title, niche, source, growth_rate, commerce_score, social_enrichment
                product_df['source'] = 'shopify'
                cols = ['product_id', 'title', 'niche', 'source', 'growth_rate', 'commerce_score', 'social_enrichment']
                product_df = product_df[cols]
                
                # Apply pagination
                total_count = len(product_df)
                if isinstance(product_df, pd.DataFrame):
                    product_df = product_df.iloc[offset:offset + limit]
                else:
                    product_df = pd.DataFrame()
                
                result = product_df.fillna("").to_dict(orient='records')  # type: ignore
                return {
                    "total_count": total_count,
                    "source": "shopify",
                    "niche": niche,
                    "limit": limit,
                    "offset": offset,
                    "returned_count": len(result),
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "data": result
                }
            
            elif source == 'amazon':
                product_df = calculate_product_level_amazon_growth(dataframes, niche)
                
                if product_df.empty:
                    return {
                        "total_count": 0,
                        "source": "amazon",
                        "niche": niche,
                        "last_updated": datetime.utcnow().isoformat() + "Z",
                        "data": []
                    }
                
                # Add niche to each record and reorder columns
                product_df['niche'] = niche
                product_df['source'] = 'amazon'
                # Reorder: product_id, title, asin, niche, source, growth_rate, commerce_score, social_enrichment
                cols = ['product_id', 'title', 'asin', 'niche', 'source', 'growth_rate', 'commerce_score', 'social_enrichment']
                product_df = product_df[cols]
                
                # Apply pagination
                total_count = len(product_df)
                if isinstance(product_df, pd.DataFrame):
                    product_df = product_df.iloc[offset:offset + limit]
                else:
                    product_df = pd.DataFrame()
                
                result = product_df.fillna("").to_dict(orient='records')  # type: ignore
                return {
                    "total_count": total_count,
                    "source": "amazon",
                    "niche": niche,
                    "limit": limit,
                    "offset": offset,
                    "returned_count": len(result),
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "data": result
                }
            
            else:  # source == 'all'
                shopify_df = calculate_product_level_shopify_growth(dataframes, niche)
                amazon_df = calculate_product_level_amazon_growth(dataframes, niche)
                
                # Add niche and source to Shopify records
                shopify_total = 0
                if not shopify_df.empty:
                    shopify_df['niche'] = niche
                    shopify_df['source'] = 'shopify'
                    cols = ['product_id', 'title', 'niche', 'source', 'growth_rate', 'commerce_score', 'social_enrichment']
                    shopify_df = shopify_df[cols]
                    shopify_total = len(shopify_df)
                    if isinstance(shopify_df, pd.DataFrame):
                        shopify_df = shopify_df.iloc[offset:offset + limit]
                    else:
                        shopify_df = pd.DataFrame()
                    shopify_result = shopify_df.fillna("").to_dict(orient='records')  # type: ignore
                else:
                    shopify_result = []
                
                # Add niche and source to Amazon records
                amazon_total = 0
                if not amazon_df.empty:
                    amazon_df['niche'] = niche
                    amazon_df['source'] = 'amazon'
                    cols = ['product_id', 'title', 'asin', 'niche', 'source', 'growth_rate', 'commerce_score', 'social_enrichment']
                    amazon_df = amazon_df[cols]
                    amazon_total = len(amazon_df)
                    if isinstance(amazon_df, pd.DataFrame):
                        amazon_df = amazon_df.iloc[offset:offset + limit]
                    else:
                        amazon_df = pd.DataFrame()
                    amazon_result = amazon_df.fillna("").to_dict(orient='records')  # type: ignore
                else:
                    amazon_result = []
                
                return {
                    "niche": niche,
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "shopify": {
                        "total_count": shopify_total,
                        "limit": limit,
                        "offset": offset,
                        "returned_count": len(shopify_result),
                        "data": shopify_result
                    },
                    "amazon": {
                        "total_count": amazon_total,
                        "limit": limit,
                        "offset": offset,
                        "returned_count": len(amazon_result),
                        "data": amazon_result
                    }
                }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating growth rate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating growth rate: {str(e)}")


# ---------- COMBINED METRICS (ALL EXCEPT GROWTH RATE) ----------
@app.get("/metrics/combined")
async def get_combined_metrics_endpoint(
    niche: Optional[str] = Query(None, description="Filter by product niche"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination")
):
    """
    Calculate and return combined niche-level analytics including Trend Index.
    
    Combines:
    - Sentiment Score
    - Engagement Rate
    - Hype Score
    - Trend Index
    
    Args:
        niche: Optional filter by product niche
        
    Returns:
        List of niches with sentiment, engagement, hype, and trend index scores
    """
    if not dataframes:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        logger.info("Calculating combined metrics (excluding growth rate)...")
        
        # Extract required dataframes
        tiktok_df = dataframes.get('tiktok_df', pd.DataFrame())
        amazon_df = dataframes.get('amazon_products_df', pd.DataFrame())
        reddit_df = dataframes.get('reddit_posts_df', pd.DataFrame())
        shopify_df = dataframes.get('shopify_variants_df', pd.DataFrame())
        
        # Calculate individual metrics
        sentiment_df = calculate_sentiment_score(dataframes)
        engagement_df = calculate_engagement(tiktok_df, reddit_df)
        hype_df = calculate_hype_score(tiktok_df, reddit_df, amazon_df, shopify_df)
        trend_df = calculate_trend_index(dataframes)
        
        # Check if any data is available
        if sentiment_df.empty and engagement_df.empty and hype_df.empty and trend_df.empty:
            return {
                "total_count": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "data": []
            }
        
        # Start with sentiment data as the base
        combined_df = sentiment_df.copy() if not sentiment_df.empty else pd.DataFrame()
        
        # Merge with engagement data
        if not engagement_df.empty:
            if combined_df.empty:
                combined_df = engagement_df.copy()
            else:
                combined_df = pd.merge(combined_df, engagement_df, on='niche', how='outer')
        
        # Merge with hype data
        if not hype_df.empty:
            if combined_df.empty:
                combined_df = hype_df.copy()
            else:
                combined_df = pd.merge(combined_df, hype_df, on='niche', how='outer')
        
        # Merge with trend data (which includes growth rate and trend index)
        if not trend_df.empty:
            if combined_df.empty:
                combined_df = trend_df.copy()
            else:
                combined_df = pd.merge(combined_df, trend_df, on='niche', how='outer')
        
        # If we still have no data, return empty result
        if combined_df.empty:
            return {
                "total_count": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "data": []
            }
        
        # Fill NaN values
        combined_df = combined_df.fillna(0)
        
        # Filter by niche if provided
        if niche:
            combined_df = combined_df[combined_df['niche'].str.lower() == niche.lower()]  # type: ignore[reportAttributeAccessIssue]
        
        # Apply pagination
        total_count = len(combined_df)
        if isinstance(combined_df, pd.DataFrame):
            combined_df = combined_df.iloc[offset:offset + limit]
        else:
            combined_df = pd.DataFrame()
        
        # Convert to records
        result = combined_df.fillna("").to_dict(orient='records')
        
        return {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "returned_count": len(result),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error calculating combined metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating combined metrics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.APP_NAME}...")
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )