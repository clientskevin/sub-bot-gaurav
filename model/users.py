from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class User(Document):
    id: int
    username: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    banned: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
