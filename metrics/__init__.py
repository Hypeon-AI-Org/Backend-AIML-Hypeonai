"""Metrics module for calculating product analytics."""

from .growth_rate import calculate_growth_rate
from .sentiment_score import calculate_sentiment_score
from .trend_index import calculate_trend_index, get_combined_metrics
from .engagement import tiktok_engagement, reddit_engagement, engagement

__all__ = [
    'calculate_growth_rate',
    'calculate_sentiment_score',
    'calculate_trend_index',
    'get_combined_metrics',
    'tiktok_engagement',
    'reddit_engagement',
    'engagement'
]