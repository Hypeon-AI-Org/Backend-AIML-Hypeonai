import pandas as pd
import os
import logging
from typing import Dict, Optional

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_all_data(sample_size: Optional[int] = None) -> Dict[str, pd.DataFrame]:
    """
    Load all data from the Data_hypeon_MVP folder with proper schema handling.
    Returns a dictionary with all dataframes needed for analysis.
    
    Args:
        sample_size: Number of rows to load per file (None for all data)
        
    Returns:
        Dictionary containing cleaned and normalized dataframes
    """
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.DATA_BASE_PATH)
    dataframes = {}
    
    try:
        # Load Shopify data
        shopify_path = os.path.join(base_path, 'Shopify_data')
        shopify_variants_file = os.path.join(shopify_path, 'cleaned_shopify_variants_data.csv')
        if os.path.exists(shopify_variants_file):
            df = pd.read_csv(shopify_variants_file, nrows=sample_size)
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            # Rename id to product_id for consistency
            if 'id' in df.columns:
                df.rename(columns={'id': 'product_id'}, inplace=True)
            dataframes['shopify_variants_df'] = df
            logger.info(f"Loaded Shopify data: {len(df)} rows")
    except Exception as e:
        logger.error(f"Error loading Shopify data: {e}")
    
    try:
        # Load Amazon data
        amazon_path = os.path.join(base_path, 'Amazon_data')
        amazon_products_file = os.path.join(amazon_path, 'products_df.csv')
        if os.path.exists(amazon_products_file):
            df = pd.read_csv(amazon_products_file, nrows=sample_size)
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            dataframes['amazon_products_df'] = df
            logger.info(f"Loaded Amazon data: {len(df)} rows")
    except Exception as e:
        logger.error(f"Error loading Amazon data: {e}")
    
    try:
        # Load TikTok data (try CSV first, then XLSX)
        tiktok_path = os.path.join(base_path, 'tiktok data', 'tiktok data')
        tiktok_csv_file = os.path.join(tiktok_path, 'tiktok_cleaned_data.csv')
        tiktok_xlsx_file = os.path.join(tiktok_path, 'tiktok_cleaned_data.xlsx')
        
        if os.path.exists(tiktok_csv_file):
            df = pd.read_csv(tiktok_csv_file, nrows=sample_size)
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            dataframes['tiktok_df'] = df
            logger.info(f"Loaded TikTok data from CSV: {len(df)} rows")
        elif os.path.exists(tiktok_xlsx_file):
            df = pd.read_excel(tiktok_xlsx_file, nrows=sample_size)
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            dataframes['tiktok_df'] = df
            logger.info(f"Loaded TikTok data from XLSX: {len(df)} rows")
        else:
            logger.warning(f"TikTok data file not found in {tiktok_path}")
    except Exception as e:
        logger.error(f"Error loading TikTok data: {e}")
    
    try:
        # Load Reddit posts
        reddit_path = os.path.join(base_path, 'reddit_data', 'reddit_data')
        reddit_posts_file = os.path.join(reddit_path, 'post', 'reddit_data_cleaned_post.xlsx')
        if os.path.exists(reddit_posts_file):
            df = pd.read_excel(reddit_posts_file, nrows=sample_size)
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            dataframes['reddit_posts_df'] = df
            logger.info(f"Loaded Reddit posts: {len(df)} rows")
    except Exception as e:
        logger.error(f"Error loading Reddit posts: {e}")
    
    try:
        # Load Reddit comments
        reddit_path = os.path.join(base_path, 'reddit_data', 'reddit_data')
        reddit_comments_file = os.path.join(reddit_path, 'comment_id', 'reddit_data_cleaned.xlsx')
        if os.path.exists(reddit_comments_file):
            df = pd.read_excel(reddit_comments_file, nrows=sample_size)
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            # Standardize column names for Reddit comments
            column_mapping = {
                'post id': 'post_id',
                'comment id': 'comment_id',
                'comment text': 'comment_text',
                'comment upvotes': 'upvotes',
                'comment author': 'author'
            }
            df.rename(columns=column_mapping, inplace=True)
            dataframes['reddit_comments_df'] = df
            logger.info(f"Loaded Reddit comments: {len(df)} rows")
    except Exception as e:
        logger.error(f"Error loading Reddit comments: {e}")
    
    return dataframes