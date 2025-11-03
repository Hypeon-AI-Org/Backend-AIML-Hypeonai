"""Configuration settings for Hypeon AI Analytics API."""

import os
from typing import Optional

class Settings:
    """Application settings and configuration."""
    
    # Application
    APP_NAME: str = "Hypeon AI Analytics API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Industry-grade API for product growth, sentiment, engagement, and trend metrics"
    
    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Data Loading
    DATA_SAMPLE_SIZE: Optional[int] = int(os.getenv("DATA_SAMPLE_SIZE", "5000"))  # None for all data
    DATA_BASE_PATH: str = os.getenv("DATA_BASE_PATH", "Data_hypeon_MVP")
    
    # Metric Weights
    # Growth Rate Weights
    GROWTH_SHOPIFY_WEIGHT: float = 0.25
    GROWTH_AMAZON_WEIGHT: float = 0.35
    GROWTH_TIKTOK_WEIGHT: float = 0.30
    GROWTH_REDDIT_WEIGHT: float = 0.10
    
    # Sentiment Weights
    SENTIMENT_AMAZON_WEIGHT: float = 0.50
    SENTIMENT_TIKTOK_WEIGHT: float = 0.30
    SENTIMENT_REDDIT_WEIGHT: float = 0.20
    
    # Engagement Weights
    ENGAGEMENT_TIKTOK_WEIGHT: float = 0.70
    ENGAGEMENT_REDDIT_WEIGHT: float = 0.30
    
    # Trend Index Weights
    TREND_GROWTH_WEIGHT: float = 0.35
    TREND_ENGAGEMENT_WEIGHT: float = 0.25
    TREND_SENTIMENT_WEIGHT: float = 0.25
    TREND_HYPE_WEIGHT: float = 0.15
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
