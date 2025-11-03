"""Sentiment score calculation module."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from textblob import TextBlob
import logging

logger = logging.getLogger(__name__)

def calculate_sentiment_score(dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Calculate sentiment score across all platforms based on text analysis.
    
    Since real data doesn't have consistent product_id, we calculate niche-level sentiment.
    
    Args:
        dataframes: Dictionary containing all loaded dataframes
        
    Returns:
        DataFrame with niche and sentiment_score columns
    """
    amazon_df = dataframes.get('amazon_products_df', pd.DataFrame())
    tiktok_df = dataframes.get('tiktok_df', pd.DataFrame())
    reddit_posts_df = dataframes.get('reddit_posts_df', pd.DataFrame())
    reddit_comments_df = dataframes.get('reddit_comments_df', pd.DataFrame())
    
    sentiments = []
    
    # Calculate Amazon Sentiment (from ratings)
    if not amazon_df.empty and 'rating' in amazon_df.columns:
        ratings = amazon_df['rating'].fillna(3.0)
        # Normalize to -1 to 1 scale (3 is neutral)
        amazon_sentiment = ((ratings.mean() - 3.0) / 2.0)
        sentiments.append({'platform': 'amazon', 'sentiment': amazon_sentiment})
    
    # Calculate TikTok Sentiment (from description)
    if not tiktok_df.empty:
        caption_sentiments = []
        # Try 'description' first (new column), fallback to 'caption_clean'
        text_col = 'description' if 'description' in tiktok_df.columns else 'caption_clean'
        
        if text_col in tiktok_df.columns:
            for caption in tiktok_df[text_col].dropna():
                try:
                    blob = TextBlob(str(caption))
                    caption_sentiments.append(blob.sentiment.polarity)  # type: ignore
                except:
                    pass
        
        if caption_sentiments:
            tiktok_sentiment = np.mean(caption_sentiments)
            sentiments.append({'platform': 'tiktok', 'sentiment': tiktok_sentiment})
    
    # Calculate Reddit Sentiment (from posts and comments)
    reddit_sentiments = []
    
    if not reddit_posts_df.empty:
        # Analyze post titles
        if 'title' in reddit_posts_df.columns:
            for title in reddit_posts_df['title'].dropna():
                try:
                    blob = TextBlob(str(title))
                    reddit_sentiments.append(blob.sentiment.polarity)  # type: ignore
                except:
                    pass
        
        # Analyze post bodies
        if 'post_body' in reddit_posts_df.columns:
            for body in reddit_posts_df['post_body'].dropna():
                try:
                    blob = TextBlob(str(body))
                    reddit_sentiments.append(blob.sentiment.polarity)  # type: ignore
                except:
                    pass
    
    if not reddit_comments_df.empty and 'comment_text' in reddit_comments_df.columns:
        for comment in reddit_comments_df['comment_text'].dropna():
            try:
                blob = TextBlob(str(comment))
                reddit_sentiments.append(blob.sentiment.polarity)  # type: ignore
            except:
                pass
    
    if reddit_sentiments:
        reddit_sentiment = np.mean(reddit_sentiments)
        sentiments.append({'platform': 'reddit', 'sentiment': reddit_sentiment})
    
    # Calculate weighted average sentiment
    if sentiments:
        weights = {
            'amazon': 0.50,
            'tiktok': 0.30,
            'reddit': 0.20
        }
        
        total_sentiment = 0
        total_weight = 0
        
        for item in sentiments:
            platform = item['platform']
            sentiment = item['sentiment']
            weight = weights.get(platform, 0)
            total_sentiment += sentiment * weight
            total_weight += weight
        
        final_sentiment = total_sentiment / total_weight if total_weight > 0 else 0
        
        # Extract niche from any available source
        niche = 'Overall'
        if not reddit_posts_df.empty and 'niche' in reddit_posts_df.columns:
            niche = reddit_posts_df['niche'].mode()[0] if len(reddit_posts_df['niche'].mode()) > 0 else 'Overall'
        
        return pd.DataFrame([{
            'niche': niche,
            'sentiment_score': final_sentiment
        }])
    
    # Return empty result if no data
    return pd.DataFrame(columns=['niche', 'sentiment_score'])

if __name__ == "__main__":
    # This section can be used for testing
    print("Sentiment score calculation module loaded successfully.")