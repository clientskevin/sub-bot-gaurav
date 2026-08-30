#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed a fake user and an active invite link whose membership has already expired.

Use this to exercise invite_link_repository.list_expired_active() and
invite_service.kick_expired() without going through the full join flow.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timedelta

from app import close_db, configs, init_db
from model import InviteLink, InviteLinkStatus
from repository import invite_link_repository, user_repository

# Defaults — override with CLI flags.
DEFAULT_FAKE_USER_ID = 9_000_000_001
DEFAULT_CHANNEL_TITLE = "Test channel (seed)"
DEFAULT_INVITE_URL = "https://t.me/+seed_expired_invite_test"


async def seed_expired_active_invite(
    *,
    user_id: int,
    channel_id: int,
    channel_title: str = DEFAULT_CHANNEL_TITLE,
    invite_link: str = DEFAULT_INVITE_URL,
    duration_seconds: int = 3600,
    expired_minutes_ago: int = 30,
    created_by: int | None = None,
) -> InviteLink:
    """Create a user (if missing) and an active invite that is already expired."""
    await init_db()
    try:
        owner_id = created_by if created_by is not None else configs.OWNER_ID

        existing_user = await user_repository.get_user_by_user_id(user_id)
        if existing_user is None:
            await user_repository.add_user(user_id)
            print(f"Created fake user id={user_id}")
        else:
            print(f"Reusing existing user id={user_id}")

        pending = await invite_link_repository.create(
            channel_id=channel_id,
            channel_title=channel_title,
            invite_link=invite_link,
            duration_seconds=duration_seconds,
            created_by=owner_id,
            invite_link_name="seed-expired-test",
        )

        joined_at = datetime.utcnow() - timedelta(
            seconds=duration_seconds + expired_minutes_ago * 60
        )
        expires_at = datetime.utcnow() - timedelta(minutes=expired_minutes_ago)

        doc = await invite_link_repository.mark_joined(
            pending.id,
            user_id,
            joined_at,
            expires_at,
        )
        if doc is None:
            raise RuntimeError("mark_joined failed after create")

        assert doc.status == InviteLinkStatus.active
        assert doc.expires_at is not None and doc.expires_at <= datetime.utcnow()

        print("Created active expired invite:")
        print(f"  link_id       = {doc.id}")
        print(f"  channel_id    = {doc.channel_id}")
        print(f"  joined_user_id= {doc.joined_user_id}")
        print(f"  joined_at     = {doc.joined_at}")
        print(f"  expires_at    = {doc.expires_at}")
        print(f"  status        = {doc.status.value}")
        return doc
    finally:
        await close_db()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed a fake user and an active-but-expired invite link."
    )
    parser.add_argument(
        "--channel-id",
        type=int,
        required=True,
        help="Telegram channel/supergroup id (e.g. -1004410054967).",
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=DEFAULT_FAKE_USER_ID,
        help=f"Fake member user id (default: {DEFAULT_FAKE_USER_ID}).",
    )
    parser.add_argument(
        "--channel-title",
        default=DEFAULT_CHANNEL_TITLE,
        help="Display title stored on the invite document.",
    )
    parser.add_argument(
        "--invite-url",
        default=DEFAULT_INVITE_URL,
        help="Stored invite URL (does not need to be a real Telegram link).",
    )
    parser.add_argument(
        "--duration-seconds",
        type=int,
        default=3600,
        help="Membership length stored on the invite (default: 3600).",
    )
    parser.add_argument(
        "--expired-minutes-ago",
        type=int,
        default=30,
        help="How far in the past expires_at should be (default: 30).",
    )
    return parser.parse_args()


async def _main() -> None:
    args = _parse_args()
    await seed_expired_active_invite(
        user_id=args.user_id,
        channel_id=args.channel_id,
        channel_title=args.channel_title,
        invite_link=args.invite_url,
        duration_seconds=args.duration_seconds,
        expired_minutes_ago=args.expired_minutes_ago,
    )


if __name__ == "__main__":
    asyncio.run(_main())
