"""Test script for authentication system."""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_crud import init_indexes


async def test_setup():
    """Test the setup of the authentication system."""
    print("Setting up authentication system...")
    init_indexes()
    print("Database indexes initialized successfully!")


if __name__ == "__main__":
    asyncio.run(test_setup())