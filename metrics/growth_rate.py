"""Growth rate calculation module with niche and product-level support."""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Literal
import logging

logger = logging.getLogger(__name__)

# Niche normalization mapping
NICHE_SYNONYMS = {
    'carpets': 'carpet',
    'curtains': 'curtain',
    'kitchen gadgets': 'kitchen_gadgets',
}

def normalize_niche(niche: str) -> str:
    """Normalize niche name to canonical form."""
    niche_lower = str(niche).strip().lower()
    return NICHE_SYNONYMS.get(niche_lower, niche_lower)


def calculate_social_enrichment(dataframes: Dict[str, pd.DataFrame], niche_filter: Optional[str] = None) -> float:
    """
    Calculate social enrichment score from TikTok and Reddit for a specific niche.
    
    Args:
        dataframes: Dictionary containing all loaded dataframes
        niche_filter: Optional niche to filter for (normalized)
        
    Returns:
        Social enrichment score (0-1 range)
    """
    tiktok_df = dataframes.get('tiktok_df', pd.DataFrame())
    reddit_posts_df = dataframes.get('reddit_posts_df', pd.DataFrame())
    reddit_comments_df = dataframes.get('reddit_comments_df', pd.DataFrame())
    
    scores = []
    
    # TikTok engagement score for niche
    if not tiktok_df.empty:
        tiktok_filtered = tiktok_df.copy()
        if niche_filter and 'niche' in tiktok_filtered.columns:
            tiktok_filtered['niche_norm'] = tiktok_filtered['niche'].apply(normalize_niche)
            tiktok_filtered = tiktok_filtered[tiktok_filtered['niche_norm'] == normalize_niche(niche_filter)]
        
        if not tiktok_filtered.empty:
            engagement_cols = ['views', 'likes', 'comments', 'shares']
            total_engagement = pd.Series([0.0] * len(tiktok_filtered))
            for col in engagement_cols:
                if col in tiktok_filtered.columns:
                    total_engagement += pd.Series(tiktok_filtered[col]).fillna(0.0)
            
            max_engagement = total_engagement.max()
            if max_engagement > 0:
                tiktok_score = (np.log1p(total_engagement) / np.log1p(max_engagement)).mean()
                scores.append(('tiktok', tiktok_score))
    
    # Reddit discussion score for niche
    if not reddit_posts_df.empty or not reddit_comments_df.empty:
        posts_filtered = reddit_posts_df.copy() if not reddit_posts_df.empty else pd.DataFrame()
        if niche_filter and not posts_filtered.empty and 'niche' in posts_filtered.columns:
            posts_filtered['niche_norm'] = posts_filtered['niche'].apply(normalize_niche)
            posts_filtered = posts_filtered[posts_filtered['niche_norm'] == normalize_niche(niche_filter)]
        
        total_posts = len(posts_filtered)
        total_comments = len(reddit_comments_df) if not reddit_comments_df.empty else 0
        total_discussion = total_posts + total_comments
        
        if total_discussion > 0:
            reddit_score = total_discussion / (total_discussion + 100)
            scores.append(('reddit', reddit_score))
    
    # Weighted combination (70% TikTok, 30% Reddit)
    if scores:
        weights = {'tiktok': 0.7, 'reddit': 0.3}
        total_score = sum(score * weights.get(platform, 0) for platform, score in scores)
        total_weight = sum(weights.get(platform, 0) for platform, _ in scores)
        return total_score / total_weight if total_weight > 0 else 0.0
    
    return 0.0


def calculate_product_level_shopify_growth(
    dataframes: Dict[str, pd.DataFrame],
    niche_filter: Optional[str] = None
) -> pd.DataFrame:
    """
    Calculate product-level growth rate for Shopify products with social enrichment.
    
    Formula: growth_rate = 0.8 * commerce_score + 0.2 * social_enrichment
    
    Args:
        dataframes: Dictionary containing all loaded dataframes
        niche_filter: Required niche filter (normalized)
        
    Returns:
        DataFrame with product_id, title, commerce_score, social_enrichment, growth_rate
    """
    if not niche_filter:
        logger.warning("Product-level Shopify growth requires niche filter")
        return pd.DataFrame(columns=['product_id', 'title', 'commerce_score', 'social_enrichment', 'growth_rate'])
    
    shopify_df = dataframes.get('shopify_variants_df', pd.DataFrame())
    
    if shopify_df.empty or 'stock_status' not in shopify_df.columns:
        return pd.DataFrame(columns=['product_id', 'title', 'commerce_score', 'social_enrichment', 'growth_rate'])
    
    # Calculate social enrichment for the niche
    social_enrichment = calculate_social_enrichment(dataframes, niche_filter)
    
    # Process Shopify data
    shopify_df = shopify_df.copy()
    
    # Calculate in-stock score per product
    shopify_df['commerce_score'] = shopify_df['stock_status'].apply(
        lambda x: 1.0 if str(x).lower() in ['in stock', 'instock', 'available'] else 0.0
    )
    
    # Ensure product_id exists
    if 'product_id' not in shopify_df.columns:
        logger.warning("Shopify data missing product_id column")
        if 'sku' in shopify_df.columns:
            shopify_df['product_id'] = shopify_df['sku']
        elif 'title' in shopify_df.columns:
            shopify_df['product_id'] = shopify_df['title']
        else:
            shopify_df['product_id'] = range(len(shopify_df))
    
    # Ensure title exists for display
    if 'title' not in shopify_df.columns:
        shopify_df['title'] = shopify_df['product_id'].astype(str)
    
    # Calculate final growth rate
    shopify_df['social_enrichment'] = social_enrichment
    shopify_df['growth_rate'] = 0.8 * shopify_df['commerce_score'] + 0.2 * social_enrichment
    
    # Return top products sorted by growth_rate
    result_df = shopify_df[['product_id', 'title', 'commerce_score', 'social_enrichment', 'growth_rate']].copy()
    result_df = result_df.sort_values(by='growth_rate', ascending=False).head(100)  # type: ignore[call-overload]
    
    return result_df


def calculate_product_level_amazon_growth(
    dataframes: Dict[str, pd.DataFrame],
    niche_filter: Optional[str] = None
) -> pd.DataFrame:
    """
    Calculate product-level growth rate for Amazon products with social enrichment.
    
    Formula: growth_rate = 0.8 * commerce_score + 0.2 * social_enrichment
    
    Args:
        dataframes: Dictionary containing all loaded dataframes
        niche_filter: Required niche filter (normalized)
        
    Returns:
        DataFrame with product_id, title, asin, commerce_score, social_enrichment, growth_rate
    """
    if not niche_filter:
        logger.warning("Product-level Amazon growth requires niche filter")
        return pd.DataFrame(columns=['product_id', 'title', 'asin', 'commerce_score', 'social_enrichment', 'growth_rate'])
    
    amazon_df = dataframes.get('amazon_products_df', pd.DataFrame())
    
    if amazon_df.empty:
        return pd.DataFrame(columns=['product_id', 'title', 'asin', 'commerce_score', 'social_enrichment', 'growth_rate'])
    
    # Calculate social enrichment for the niche
    social_enrichment = calculate_social_enrichment(dataframes, niche_filter)
    
    # Process Amazon data
    amazon_df = amazon_df.copy()
    
    # Calculate commerce score using reviews and rating
    if 'reviews_count' in amazon_df.columns:
        review_counts = amazon_df['reviews_count'].fillna(0)
        max_reviews = review_counts.max()
        if max_reviews > 0:
            amazon_df['commerce_score'] = np.log1p(review_counts) / np.log1p(max_reviews)
        else:
            amazon_df['commerce_score'] = 0.0
    elif 'rating' in amazon_df.columns:
        ratings = amazon_df['rating'].fillna(3.0)
        amazon_df['commerce_score'] = ((ratings - 3.0) / 2.0).clip(0, 1)
    else:
        amazon_df['commerce_score'] = 0.0
    
    # Ensure required columns exist
    if 'product_id' not in amazon_df.columns:
        logger.warning("Amazon data missing product_id column")
        if 'asin' in amazon_df.columns:
            amazon_df['product_id'] = amazon_df['asin']
        elif 'title' in amazon_df.columns:
            amazon_df['product_id'] = amazon_df['title']
        else:
            amazon_df['product_id'] = range(len(amazon_df))
    
    if 'title' not in amazon_df.columns:
        amazon_df['title'] = amazon_df['product_id'].astype(str)
    
    if 'asin' not in amazon_df.columns:
        amazon_df['asin'] = amazon_df['product_id'].astype(str)
    
    # Calculate final growth rate
    amazon_df['social_enrichment'] = social_enrichment
    amazon_df['growth_rate'] = 0.8 * amazon_df['commerce_score'] + 0.2 * social_enrichment
    
    # Return top products sorted by growth_rate
    result_df = amazon_df[['product_id', 'title', 'asin', 'commerce_score', 'social_enrichment', 'growth_rate']].copy()
    result_df = result_df.sort_values(by='growth_rate', ascending=False).head(100)  # type: ignore[call-overload]
    
    return result_df


def calculate_growth_rate(dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Calculate growth rate for products based on multiple platform signals.
    
    Metrics used:
    - Shopify: Stock availability (binary signal)
    - Amazon: Reviews count and rating (engagement proxy)
    - TikTok: Total engagement (views, likes, comments, shares)
    - Reddit: Discussion volume (posts + comments by niche)
    
    Args:
        dataframes: Dictionary containing all loaded dataframes
        
    Returns:
        DataFrame with niche and growth_rate columns
    """
    # Get dataframes
    shopify_df = dataframes.get('shopify_variants_df', pd.DataFrame())
    amazon_df = dataframes.get('amazon_products_df', pd.DataFrame())
    tiktok_df = dataframes.get('tiktok_df', pd.DataFrame())
    reddit_posts_df = dataframes.get('reddit_posts_df', pd.DataFrame())
    reddit_comments_df = dataframes.get('reddit_comments_df', pd.DataFrame())
    
    results = []
    
    # Calculate Shopify Growth Rate (by stock availability)
    if not shopify_df.empty and 'stock_status' in shopify_df.columns:
        shopify_df = shopify_df.copy()
        # Calculate in-stock percentage as growth signal
        shopify_df['in_stock'] = shopify_df['stock_status'].apply(
            lambda x: 1 if str(x).lower() in ['in stock', 'instock', 'available'] else 0
        )
        shopify_growth = shopify_df['in_stock'].mean()
        results.append({'platform': 'shopify', 'growth': shopify_growth})
    
    # Calculate Amazon Growth Rate (by review activity)
    if not amazon_df.empty:
        amazon_df = amazon_df.copy()
        amazon_growth = 0
        
        if 'reviews_count' in amazon_df.columns:
            # Normalize review count using log scaling
            review_counts = amazon_df['reviews_count'].fillna(0)
            max_reviews = review_counts.max()
            if max_reviews > 0:
                norm_reviews = np.log1p(review_counts) / np.log1p(max_reviews)
                amazon_growth = norm_reviews.mean()
        
        if 'rating' in amazon_df.columns and amazon_growth == 0:
            # Fallback to rating if no reviews
            ratings = amazon_df['rating'].fillna(3.0)
            amazon_growth = (ratings.mean() - 3.0) / 2.0  # Normalize to 0-1
        
        results.append({'platform': 'amazon', 'growth': max(0, amazon_growth)})
    
    # Calculate TikTok Growth Rate (by engagement)
    if not tiktok_df.empty:
        tiktok_df = tiktok_df.copy()
        engagement_cols = ['views', 'likes', 'comments', 'shares']
        
        # Calculate total engagement
        total_engagement = pd.Series([0.0] * len(tiktok_df))
        for col in engagement_cols:
            if col in tiktok_df.columns:
                total_engagement += tiktok_df[col].fillna(0.0)
        
        # Normalize using log scaling
        max_engagement = total_engagement.max()
        if max_engagement > 0:
            tiktok_growth = (np.log1p(total_engagement) / np.log1p(max_engagement)).mean()
            results.append({'platform': 'tiktok', 'growth': tiktok_growth})
    
    # Calculate Reddit Growth Rate (by discussion volume)
    if not reddit_posts_df.empty or not reddit_comments_df.empty:
        total_posts = len(reddit_posts_df) if not reddit_posts_df.empty else 0
        total_comments = len(reddit_comments_df) if not reddit_comments_df.empty else 0
        total_discussion = total_posts + total_comments
        
        # Normalize to 0-1 range using sigmoid-like function
        reddit_growth = total_discussion / (total_discussion + 100)  # Asymptotic to 1
        results.append({'platform': 'reddit', 'growth': reddit_growth})
    
    # Calculate weighted average growth rate
    if results:
        weights = {
            'shopify': 0.25,
            'amazon': 0.35,
            'tiktok': 0.30,
            'reddit': 0.10
        }
        
        total_growth = 0
        total_weight = 0
        
        for result in results:
            platform = result['platform']
            growth = result['growth']
            weight = weights.get(platform, 0)
            total_growth += growth * weight
            total_weight += weight
        
        final_growth = total_growth / total_weight if total_weight > 0 else 0
        
        # Since we don't have product_id in the real data, we'll return niche-level metrics
        # Extract niche from any available source
        niche = 'Overall'
        if not reddit_posts_df.empty and 'niche' in reddit_posts_df.columns:
            niche = reddit_posts_df['niche'].mode()[0] if len(reddit_posts_df['niche'].mode()) > 0 else 'Overall'
        
        return pd.DataFrame([{
            'niche': niche,
            'growth_rate': final_growth
        }])
    
    # Return empty result if no data
    return pd.DataFrame(columns=['niche', 'growth_rate'])

if __name__ == "__main__":
    # This section can be used for testing
    print("Growth rate calculation module loaded successfully.")