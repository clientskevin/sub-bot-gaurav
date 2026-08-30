from typing import Optional

from beanie import init_beanie
from pymongo import AsyncMongoClient

from model import Admin, InviteLink, LogTopic, User

from .config import configs

client: Optional[AsyncMongoClient] = None


async def init_db():
    """Connect to MongoDB and initialize Beanie document models."""
    global client
    client = AsyncMongoClient(configs.DATABASE_URL)
    await init_beanie(
        database=client[configs.DATABASE_NAME],
        document_models=[User, Admin, LogTopic, InviteLink],
    )


async def close_db():
    """Close the MongoDB client connection."""
    if client:
        await client.close()
