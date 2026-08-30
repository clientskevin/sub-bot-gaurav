from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field

from .enums import InviteLinkStatus


class InviteLink(Document):
    channel_id: int
    channel_title: str
    invite_link: str
    invite_link_name: Optional[str] = None
    duration_seconds: int
    created_by: int
    status: InviteLinkStatus = InviteLinkStatus.pending
    joined_user_id: Optional[int] = None
    joined_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "invite_links"
