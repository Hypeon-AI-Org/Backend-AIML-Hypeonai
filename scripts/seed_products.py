import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def seed():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    path = os.path.join(os.path.dirname(__file__), "../data/products.json")
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    await db.products.delete_many({})
    # ensure docs follow schema - minimal sanitization
    for it in items:
        await db.products.insert_one(it)
    print("Seeded", len(items))
    client.close()

if __name__ == "__main__":
    asyncio.run(seed())