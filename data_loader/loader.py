import pandas as pd
import os

def load_all_data(sample_size=1000):
    """
    Load all data from the Data_hypeon_MVP folder.
    Returns a dictionary with all dataframes needed for analysis.
    """
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data_hypeon_MVP')
    
    # Initialize dictionary to hold all dataframes
    dataframes = {}
    
    # Load Shopify data - specifically the variants data
    shopify_path = os.path.join(base_path, 'Shopify_data')
    if os.path.exists(shopify_path):
        shopify_variants_file = os.path.join(shopify_path, 'cleaned_shopify_variants_data.csv')
        if os.path.exists(shopify_variants_file):
            # Load only a sample for testing
            dataframes['shopify_variants_df'] = pd.read_csv(shopify_variants_file, nrows=sample_size)
    
    # Load Amazon data - specifically the products data
    amazon_path = os.path.join(base_path, 'Amazon_data')
    if os.path.exists(amazon_path):
        amazon_products_file = os.path.join(amazon_path, 'products_df.csv')
        if os.path.exists(amazon_products_file):
            # Load only a sample for testing
            dataframes['amazon_products_df'] = pd.read_csv(amazon_products_file, nrows=sample_size)
    
    # Load TikTok data - Excel file
    tiktok_path = os.path.join(base_path, 'tiktok data', 'tiktok data')
    if os.path.exists(tiktok_path):
        tiktok_file = os.path.join(tiktok_path, 'tiktok_cleaned_data.xlsx')
        if os.path.exists(tiktok_file):
            # Load only a sample for testing
            dataframes['tiktok_df'] = pd.read_excel(tiktok_file, nrows=sample_size)
    
    # Load Reddit data (posts and comments) - Excel files
    reddit_path = os.path.join(base_path, 'reddit_data', 'reddit_data')
    if os.path.exists(reddit_path):
        # Load posts
        reddit_posts_file = os.path.join(reddit_path, 'post', 'reddit_data_cleaned_post.xlsx')
        if os.path.exists(reddit_posts_file):
            # Load only a sample for testing
            dataframes['reddit_posts_df'] = pd.read_excel(reddit_posts_file, nrows=sample_size)
        
        # Load comments
        reddit_comments_file = os.path.join(reddit_path, 'comment_id', 'reddit_data_cleaned.xlsx')
        if os.path.exists(reddit_comments_file):
            # Load only a sample for testing
            dataframes['reddit_comments_df'] = pd.read_excel(reddit_comments_file, nrows=sample_size)
    
    return dataframes