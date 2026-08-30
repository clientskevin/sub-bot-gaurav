from datetime import datetime

from beanie import Document
from pydantic import Field


class Admin(Document):
    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "admins"
