import pandas as pd
import logging
from typing import Dict, Optional

from database.mongo_connection import get_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_all_data(sample_size: Optional[int] = None) -> Dict[str, pd.DataFrame]:
    """
    Load all data from MongoDB cluster with proper schema handling.
    Returns a dictionary with all dataframes needed for analysis.
    
    Args:
        sample_size: Number of documents to load per collection (None for all data)
        
    Returns:
        Dictionary containing cleaned and normalized dataframes
    """
    dataframes = {}
    
    # Collection mapping: MongoDB collection name -> DataFrame key
    collection_mapping = {
        "shopify_variants": "shopify_variants_df",
        "amazon_products": "amazon_products_df",
        "tiktok_data": "tiktok_df",
        "reddit_posts": "reddit_posts_df",
        "reddit_comments": "reddit_comments_df"
    }
    
    for collection_name, df_key in collection_mapping.items():
        try:
            # Get collection from MongoDB
            collection = get_collection(collection_name)
            
            # Query with optional limit
            if sample_size is not None:
                cursor = collection.find().limit(sample_size)
            else:
                cursor = collection.find()
            
            # Convert to list and then to DataFrame
            documents = list(cursor)
            count = len(documents)
            
            if count == 0:
                logger.warning(f"Collection '{collection_name}' is empty")
                dataframes[df_key] = pd.DataFrame()
            else:
                # Convert to DataFrame
                df = pd.DataFrame(documents)
                
                # Convert _id field to string if it exists
                if '_id' in df.columns:
                    df['_id'] = df['_id'].astype(str)
                
                # Normalize all column names to lowercase
                df.columns = df.columns.str.strip().str.lower()
                
                dataframes[df_key] = df
                logger.info(f"Loaded {count} records from MongoDB collection: {collection_name}")
                
        except Exception as e:
            logger.error(f"Error loading data from collection '{collection_name}': {e}", exc_info=True)
            # Return empty DataFrame on error
            dataframes[df_key] = pd.DataFrame()
    
    return dataframes