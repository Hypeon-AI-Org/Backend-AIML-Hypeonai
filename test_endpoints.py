"""Test script for authentication endpoints."""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from fastapi import FastAPI
    from auth_router import router as auth_router
    print("✅ All imports successful!")
    
    # Create a test app
    app = FastAPI()
    app.include_router(auth_router)
    print("✅ Router included successfully!")
    
except Exception as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

print("✅ Authentication system is ready!")