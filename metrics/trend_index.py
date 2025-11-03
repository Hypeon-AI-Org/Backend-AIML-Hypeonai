"""Trend index calculation module."""

import pandas as pd
import numpy as np
from typing import Dict
import logging

from .growth_rate import calculate_growth_rate
from .sentiment_score import calculate_sentiment_score
from .engagement import engagement as calculate_engagement

logger = logging.getLogger(__name__)

def calculate_trend_index(dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Calculate comprehensive trend index combining all metrics.
    
    Formula:
    TrendIndex = 0.35*GrowthRate + 0.25*EngagementRate + 0.25*SentimentScore + 0.15*HypeScore
    
    Args:
        dataframes: Dictionary containing all loaded dataframes
        
    Returns:
        DataFrame with niche and all metric scores including trend_index (0-100)
    """
    # Calculate individual metrics
    growth_df = calculate_growth_rate(dataframes)
    sentiment_df = calculate_sentiment_score(dataframes)
    
    # Calculate engagement
    tiktok_df = dataframes.get('tiktok_df', pd.DataFrame())
    reddit_posts_df = dataframes.get('reddit_posts_df', pd.DataFrame())
    engagement_df = calculate_engagement(tiktok_df, reddit_posts_df)
    
    # Merge all metrics
    if not growth_df.empty and not sentiment_df.empty and not engagement_df.empty:
        # Merge on niche
        result_df = growth_df.merge(sentiment_df, on='niche', how='outer')
        result_df = result_df.merge(engagement_df, on='niche', how='outer')
        result_df = result_df.fillna(0)
        
        # Normalize growth_rate to 0-1 (it should already be)
        growth_norm = result_df['growth_rate']
        
        # Normalize engagement to 0-1 (should already be from engagement metric)
        engagement_norm = result_df.get('engagement_final', pd.Series([0.5] * len(result_df)))
        if not isinstance(engagement_norm, pd.Series):
            engagement_norm = pd.Series([0.5] * len(result_df))
        
        # Normalize sentiment from -1 to 1 to 0 to 1 scale
        sentiment_norm = (result_df['sentiment_score'] + 1) / 2
        
        # Simplified Hype Score (based on creation recency proxy)
        # For MVP, use a constant or derive from available data
        hype_score = 0.5  # Placeholder
        
        # Calculate Trend Index
        result_df['trend_index'] = (
            0.35 * growth_norm +
            0.25 * engagement_norm +
            0.25 * sentiment_norm +
            0.15 * hype_score
        )
        
        # Scale to 0-100
        result_df['trend_index'] = result_df['trend_index'] * 100
        result_df['trend_index'] = result_df['trend_index'].clip(0, 100)
        
        return pd.DataFrame(result_df[['niche', 'growth_rate', 'sentiment_score', 'trend_index']])
    
    # Return empty result if insufficient data
    return pd.DataFrame(columns=['niche', 'growth_rate', 'sentiment_score', 'trend_index'])

def get_combined_metrics(dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Get all metrics in one dataframe for the /metrics/trend endpoint.
    
    Args:
        dataframes: Dictionary containing all loaded dataframes
        
    Returns:
        DataFrame with niche, growth_rate, sentiment_score, and trend_index columns
    """
    return calculate_trend_index(dataframes)

if __name__ == "__main__":
    # This section can be used for testing
    print("Trend index calculation module loaded successfully.")