"""Engagement metrics calculation module."""

import pandas as pd
import numpy as np
from typing import Dict


def normalize(series: pd.Series) -> pd.Series:
    """Normalize safely between 0–1."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([0.5] * len(series))
    return (series - min_val) / (max_val - min_val)


# ---------- TikTok ----------
def tiktok_engagement(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate TikTok engagement rate by niche."""
    try:
        if df.empty:
            return pd.DataFrame(columns=['niche', 'tiktok_eng'])
        
        df = df.copy()
        
        # Check if niche column exists
        if 'niche' not in df.columns:
            # Fallback to overall if no niche
            df['tiktok_eng'] = (df['likes'] + df['comments'] + df['shares']) / df['views'].replace(0, np.nan)
            df['tiktok_eng'] = df['tiktok_eng'].replace([np.inf, -np.inf], 0).fillna(0)
            avg_engagement = df['tiktok_eng'].mean()
            return pd.DataFrame([{'niche': 'overall', 'tiktok_eng': avg_engagement}])
        
        # Normalize niche names
        df['niche'] = df['niche'].str.strip().str.lower()

        # Per-video engagement rate
        df['tiktok_eng'] = (df['likes'] + df['comments'] + df['shares']) / df['views'].replace(0, np.nan)
        df['tiktok_eng'] = df['tiktok_eng'].replace([np.inf, -np.inf], 0).fillna(0)

        # Average per video, then per niche
        video_avg = df.groupby(['niche', 'video_id'], as_index=False)['tiktok_eng'].mean()
        niche_avg = video_avg.groupby('niche', as_index=False)['tiktok_eng'].mean()

        return pd.DataFrame(niche_avg[['niche', 'tiktok_eng']])

    except Exception as e:
        print(f"Error in TikTok engagement: {e}")
        return pd.DataFrame(columns=['niche', 'tiktok_eng'])


# ---------- Reddit ----------
def reddit_engagement(posts_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Reddit engagement rate by niche."""
    try:
        if posts_df.empty:
            return pd.DataFrame(columns=['niche', 'reddit_eng'])
        
        posts_df = posts_df.copy()
        
        # Normalize niche names
        if 'niche' not in posts_df.columns:
            posts_df['niche'] = 'overall'
        else:
            posts_df['niche'] = posts_df['niche'].str.strip().str.lower()

        # Reddit engagement: (upvotes + comments) per post
        upvotes_col = posts_df['upvotes'] if 'upvotes' in posts_df.columns else pd.Series([0] * len(posts_df))
        comments_col = posts_df['comments_count'] if 'comments_count' in posts_df.columns else pd.Series([0] * len(posts_df))
        posts_df['reddit_eng'] = (upvotes_col + comments_col) / (comments_col + 1)
        posts_df['reddit_eng'] = posts_df['reddit_eng'].replace([np.inf, -np.inf], 0).fillna(0)

        # Average by niche
        niche_avg = posts_df.groupby('niche', as_index=False)['reddit_eng'].mean()

        return pd.DataFrame(niche_avg[['niche', 'reddit_eng']])

    except Exception as e:
        print(f"Error in Reddit engagement: {e}")
        return pd.DataFrame(columns=['niche', 'reddit_eng'])


# ---------- Combine ----------
def engagement(tiktok_df: pd.DataFrame, reddit_df: pd.DataFrame) -> pd.DataFrame:
    """Combine TikTok and Reddit engagement metrics."""
    try:
        # Calculate individual engagements
        tiktok_eng_df = tiktok_engagement(tiktok_df)
        reddit_eng_df = reddit_engagement(reddit_df)
        
        if tiktok_eng_df.empty and reddit_eng_df.empty:
            return pd.DataFrame(columns=['niche', 'engagement_final'])

        # Normalize niche names
        if not tiktok_eng_df.empty:
            tiktok_eng_df['niche'] = tiktok_eng_df['niche'].str.strip().str.lower()
        if not reddit_eng_df.empty:
            reddit_eng_df['niche'] = reddit_eng_df['niche'].str.strip().str.lower()

        # Merge
        combined = pd.merge(tiktok_eng_df, reddit_eng_df, on='niche', how='outer').fillna(0)

        # Normalize both engagement sources
        for col in ['tiktok_eng', 'reddit_eng']:
            if col in combined.columns:
                combined[col] = normalize(pd.Series(combined[col]))

        # Weighted average (TikTok 70%, Reddit 30%)
        tiktok_weight = 0.7
        reddit_weight = 0.3
        
        tiktok_col = combined['tiktok_eng'] if 'tiktok_eng' in combined.columns else pd.Series([0] * len(combined))
        reddit_col = combined['reddit_eng'] if 'reddit_eng' in combined.columns else pd.Series([0] * len(combined))
        
        combined['engagement_final'] = tiktok_weight * pd.Series(tiktok_col) + reddit_weight * pd.Series(reddit_col)

        # Normalize final result
        combined['engagement_final'] = normalize(pd.Series(combined['engagement_final']))

        return pd.DataFrame(combined[['niche', 'engagement_final']])

    except Exception as e:
        print(f"Error combining engagement: {e}")
        return pd.DataFrame(columns=['niche', 'engagement_final'])
