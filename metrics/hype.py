import pandas as pd
import numpy as np
from typing import Dict, Optional
from metrics.engagement import engagement
from metrics.sentiment_score import calculate_sentiment_score


# ---------- Utility ----------
def normalize(series):
    """Normalize safely between 0.2–1.0 for stability."""
    s = (series - series.min()) / (series.max() - series.min() + 1e-9)
    return 0.2 + 0.8 * s  # avoids collapse near 0


# ---------- Hype Score ----------
def calculate_hype_score(tiktok_df: pd.DataFrame, reddit_df: pd.DataFrame, amazon_df: pd.DataFrame, shopify_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Combine Engagement + Sentiment to compute final Hype Score.
    Inputs:
        - tiktok_df: TikTok data with 'niche', engagement + description columns
        - reddit_df: Reddit posts/comments with 'niche', upvotes, text columns
        - amazon_df: Amazon reviews with 'product_id', 'rating', text
        - shopify_df (optional): for niche-level mapping or trend signals

    Output:
        DataFrame ['niche', 'engagement_final', 'sentiment_score', 'hype_score']
    """

    # ---------- Step 1: Engagement ----------
    engage_df = engagement(tiktok_df=tiktok_df, reddit_df=reddit_df)

    # Drop invalid niches if present
    engage_df = engage_df[engage_df['niche'].notna() & (engage_df['niche'] != 0)]

    # ---------- Step 2: Sentiment ----------
    # Build dataframes dict for sentiment calculation
    dataframes = {
        'tiktok_df': tiktok_df,
        'amazon_products_df': amazon_df,
        'reddit_posts_df': reddit_df,
        'reddit_comments_df': pd.DataFrame()  # Empty if not provided
    }
    
    sent_df = calculate_sentiment_score(dataframes)

    # Drop invalid niches
    sent_df = sent_df[sent_df['niche'].notna() & (sent_df['niche'] != 0)]

    # ---------- Step 3: Merge ----------
    hype_df = pd.merge(engage_df, sent_df, on="niche", how="outer").fillna(0)

    # ---------- Step 4: Weighted Hype ----------
    hype_df["hype_score_raw"] = (
        0.6 * hype_df["engagement_final"] +
        0.8 * hype_df["sentiment_score"]
    )

    # ---------- Step 5: Normalize final hype score ----------
    hype_df["hype_score"] = normalize(hype_df["hype_score_raw"])

    # ---------- Step 6: Sort ----------
    hype_df = hype_df.sort_values("hype_score", ascending=False).reset_index(drop=True)

    return pd.DataFrame(hype_df[["niche", "hype_score"]])
