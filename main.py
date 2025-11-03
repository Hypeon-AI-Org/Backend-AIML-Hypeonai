"""Main FastAPI application for Hypeon AI Metrics."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any, Literal
import pandas as pd
import logging
from datetime import datetime

from data_loader import load_all_data
from metrics.growth_rate import (
    calculate_growth_rate,
    calculate_product_level_shopify_growth,
    calculate_product_level_amazon_growth
)
from metrics.sentiment_score import calculate_sentiment_score
from metrics.trend_index import get_combined_metrics
from metrics.engagement import engagement as calculate_engagement
from metrics.hype import calculate_hype_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hypeon AI Analytics API",
    description="Industry-grade API for product growth, sentiment, engagement, and trend metrics",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data store
dataframes: Dict[str, pd.DataFrame] = {}

@app.on_event("startup")
async def load_data():
    """Load all data at application startup."""
    global dataframes
    try:
        logger.info("Loading data from Data_hypeon_MVP...")
        # Load real data (use sample_size=None for production, or set a limit for dev)
        dataframes = load_all_data(sample_size=5000)  # Adjust sample_size as needed
        
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
            "/metrics/sentiment",
            "/metrics/engagement",
            "/metrics/trend",
            "/metrics/hype",
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
    source: Literal['shopify', 'amazon', 'all'] = Query('all', description="Data source: 'shopify', 'amazon', or 'all' (only for product-level)")
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
                growth_df = growth_df[growth_df['niche'].str.lower() == niche.lower()]
            
            # Convert to records
            result = growth_df.fillna("").to_dict(orient='records')  # type: ignore
            
            return {
                "total_count": len(result),
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
                
                result = product_df.fillna("").to_dict(orient='records')  # type: ignore
                return {
                    "total_count": len(result),
                    "source": "shopify",
                    "niche": niche,
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "limit": 100,
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
                
                result = product_df.fillna("").to_dict(orient='records')  # type: ignore
                return {
                    "total_count": len(result),
                    "source": "amazon",
                    "niche": niche,
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "limit": 100,
                    "data": result
                }
            
            else:  # source == 'all'
                shopify_df = calculate_product_level_shopify_growth(dataframes, niche)
                amazon_df = calculate_product_level_amazon_growth(dataframes, niche)
                
                # Add niche and source to Shopify records
                if not shopify_df.empty:
                    shopify_df['niche'] = niche
                    shopify_df['source'] = 'shopify'
                    cols = ['product_id', 'title', 'niche', 'source', 'growth_rate', 'commerce_score', 'social_enrichment']
                    shopify_df = shopify_df[cols]
                    shopify_result = shopify_df.fillna("").to_dict(orient='records')  # type: ignore
                else:
                    shopify_result = []
                
                # Add niche and source to Amazon records
                if not amazon_df.empty:
                    amazon_df['niche'] = niche
                    amazon_df['source'] = 'amazon'
                    cols = ['product_id', 'title', 'asin', 'niche', 'source', 'growth_rate', 'commerce_score', 'social_enrichment']
                    amazon_df = amazon_df[cols]
                    amazon_result = amazon_df.fillna("").to_dict(orient='records')  # type: ignore
                else:
                    amazon_result = []
                
                return {
                    "niche": niche,
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "shopify": {
                        "total_count": len(shopify_result),
                        "limit": 100,
                        "data": shopify_result
                    },
                    "amazon": {
                        "total_count": len(amazon_result),
                        "limit": 100,
                        "data": amazon_result
                    }
                }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating growth rate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating growth rate: {str(e)}")


@app.get("/metrics/hype")
async def get_hype_score(
    niche: Optional[str] = Query(None, description="Filter by niche")
):
    """
    Calculate and return hype score metrics.
    
    Hype score combines:
    - Engagement (60%): TikTok and Reddit engagement metrics
    - Sentiment (80%): Multi-platform sentiment analysis
    
    Formula: hype_score = 0.6 * engagement + 0.8 * sentiment (normalized 0.2-1.0)
    
    Args:
        niche: Optional filter by niche
        
    Returns:
        List of niches with hype scores (0.2-1.0)
    """
    if not dataframes:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        logger.info("Calculating hype scores...")
        tiktok_df = dataframes.get('tiktok_df', pd.DataFrame())
        reddit_df = dataframes.get('reddit_posts_df', pd.DataFrame())
        amazon_df = dataframes.get('amazon_products_df', pd.DataFrame())
        
        if tiktok_df.empty and reddit_df.empty and amazon_df.empty:
            return {
                "total_count": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "data": []
            }
        
        hype_df = calculate_hype_score(
            tiktok_df=tiktok_df,
            reddit_df=reddit_df,
            amazon_df=amazon_df
        )
        
        if hype_df.empty:
            return {
                "total_count": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "data": []
            }
        
        # Filter by niche if provided
        if niche:
            hype_df = hype_df[hype_df['niche'].str.lower() == niche.lower()]
        
        # Convert to records and handle NaN values
        result = hype_df.fillna("").to_dict(orient='records')  # type: ignore
        
        return {
            "total_count": len(result),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error calculating hype score: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating hype score: {str(e)}")


@app.get("/metrics/sentiment")
async def get_sentiment_score(niche: Optional[str] = Query(None, description="Filter by product niche")):
    """
    Calculate and return sentiment score metrics.
    
    Sentiment analysis combines:
    - Amazon product ratings and review text
    - TikTok caption sentiment
    - Reddit post and comment sentiment
    
    Args:
        niche: Optional filter by product niche
        
    Returns:
        List of products with sentiment scores (-1 to 1)
    """
    if not dataframes:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        logger.info("Calculating sentiment scores...")
        sentiment_df = calculate_sentiment_score(dataframes)
        
        if sentiment_df.empty:
            return {
                "total_count": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "data": []
            }
        
        # Filter by niche if provided
        if niche:
            sentiment_df = sentiment_df[sentiment_df['niche'].str.lower() == niche.lower()]
        
        # Convert to records and handle NaN values
        result = sentiment_df.fillna("").to_dict(orient='records')  # type: ignore
        
        return {
            "total_count": len(result),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error calculating sentiment score: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating sentiment score: {str(e)}")


@app.get("/metrics/engagement")
async def get_engagement(niche: Optional[str] = Query(None, description="Filter by niche")):
    """
    Calculate and return engagement metrics.
    
    Engagement combines:
    - TikTok: (likes + comments + shares) / views
    - Reddit: (upvotes + comments) per post
    
    Weighted: 70% TikTok, 30% Reddit
    
    Args:
        niche: Optional filter by niche
        
    Returns:
        List of niches with engagement scores (0-1)
    """
    if not dataframes:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        logger.info("Calculating engagement metrics...")
        tiktok_df = dataframes.get('tiktok_df', pd.DataFrame())
        reddit_posts_df = dataframes.get('reddit_posts_df', pd.DataFrame())
        
        if tiktok_df.empty and reddit_posts_df.empty:
            return {
                "total_count": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "data": []
            }
        
        engagement_df = calculate_engagement(tiktok_df, reddit_posts_df)
        
        if engagement_df.empty:
            return {
                "total_count": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "data": []
            }
        
        # Filter by niche if provided
        if niche and isinstance(engagement_df, pd.DataFrame):
            engagement_df = engagement_df[engagement_df['niche'].str.lower() == niche.lower()]
        
        # Convert to records and handle NaN values
        if isinstance(engagement_df, pd.DataFrame):
            result = engagement_df.fillna("").to_dict(orient='records')  # type: ignore
        else:
            result = []
        
        return {
            "total_count": len(result),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error calculating engagement: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating engagement: {str(e)}")


@app.get("/metrics/trend")
async def get_trend_index(niche: Optional[str] = Query(None, description="Filter by product niche")):
    """
    Calculate and return comprehensive trend index.
    
    Trend index combines:
    - Growth Rate (35%)
    - Engagement Rate (25%)
    - Sentiment Score (25%)
    - Hype Score (15%)
    
    Args:
        niche: Optional filter by product niche
        
    Returns:
        List of products with all metrics and trend index (0-100)
    """
    if not dataframes:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        logger.info("Calculating trend index...")
        trend_df = get_combined_metrics(dataframes)
        
        if trend_df.empty:
            return {
                "total_count": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "data": []
            }
        
        # Filter by niche if provided
        if niche:
            trend_df = trend_df[trend_df['niche'].str.lower() == niche.lower()]
        
        # Convert to records and handle NaN values
        result = trend_df.fillna("").to_dict(orient='records')  # type: ignore
        
        return {
            "total_count": len(result),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error calculating trend index: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating trend index: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Hypeon AI Analytics API...")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )