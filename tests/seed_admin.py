#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed an admin by Telegram user id or @username.

Examples:
  python -m tests.seed_admin --user krmg_priceaction
  python -m tests.seed_admin --user @krmg_priceaction
  python -m tests.seed_admin --user 123456789
"""

from __future__ import annotations

import argparse
import asyncio

from pyrogram.client import Client
from pyrogram.types import User

from app import close_db, configs, init_db
from service import add_admin


def _as_user(response: User | list[User]) -> User:
    if isinstance(response, list):
        return response[0]
    return response


def _parse_ref(raw: str) -> int | str:
    raw = raw.strip()
    if raw.isdigit():
        return int(raw)
    return raw.lstrip("@")


async def seed_admin(ref: int | str) -> None:
    await init_db()
    # Bare client (no plugins) so we only resolve the user + write Mongo.
    client = Client(
        "seed_admin",
        api_id=configs.API_ID,
        api_hash=configs.API_HASH,
        bot_token=configs.BOT_TOKEN,
        in_memory=True,
    )
    try:
        await client.start()
        user = _as_user(await client.get_users(ref))
        added = await add_admin(user.id)
        label = f"@{user.username}" if user.username else str(user.id)
        if added:
            print(f"Added admin {label} (id={user.id})")
        else:
            print(f"Already admin {label} (id={user.id})")
    finally:
        if client.is_connected:
            await client.stop()
        await close_db()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed a bot admin.")
    parser.add_argument(
        "--user",
        required=True,
        help="Telegram user id or @username (e.g. krmg_priceaction).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(seed_admin(_parse_ref(args.user)))
