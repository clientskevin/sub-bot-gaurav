#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: invite_link.py
Author: Maria Kevin
Created: 2026-08-27
Description: Invite link repository using Beanie.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from datetime import datetime
from typing import Optional

from model import InviteLink, InviteLinkStatus


class InviteLinkRepository:
    async def create(
        self,
        channel_id: int,
        channel_title: str,
        invite_link: str,
        duration_seconds: int,
        created_by: int,
        invite_link_name: Optional[str] = None,
    ) -> InviteLink:
        """Insert a new pending invite link document."""
        doc = InviteLink(
            channel_id=channel_id,
            channel_title=channel_title,
            invite_link=invite_link,
            invite_link_name=invite_link_name,
            duration_seconds=duration_seconds,
            created_by=created_by,
            status=InviteLinkStatus.pending,
        )
        await doc.insert()
        return doc

    async def get_by_invite_link(self, url: str) -> Optional[InviteLink]:
        """Fetch an invite link document by its Telegram URL."""
        return await InviteLink.find_one(InviteLink.invite_link == url)

    async def mark_joined(
        self,
        link_id,
        user_id: int,
        joined_at: datetime,
        expires_at: datetime,
    ) -> Optional[InviteLink]:
        """Mark a pending invite as active after a member joins."""
        doc = await InviteLink.get(link_id)
        if not doc:
            return None
        doc.status = InviteLinkStatus.active
        doc.joined_user_id = user_id
        doc.joined_at = joined_at
        doc.expires_at = expires_at
        await doc.save()
        return doc

    async def list_expired_active(self, now: datetime) -> list[InviteLink]:
        """Return active invite links whose membership has expired."""
        return await InviteLink.find(
            InviteLink.status == InviteLinkStatus.active,
            InviteLink.expires_at <= now,
        ).to_list()

    async def mark_expired(self, link_id) -> Optional[InviteLink]:
        """Mark an invite link as expired after the member is kicked."""
        doc = await InviteLink.get(link_id)
        if not doc:
            return None
        doc.status = InviteLinkStatus.expired
        await doc.save()
        return doc


invite_link_repository = InviteLinkRepository()
