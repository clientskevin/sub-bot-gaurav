#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: on_join_request.py
Author: Maria Kevin
Created: 2026-08-27
Description: Handle chat join requests for tracked invite links.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from loguru import logger
from pyrogram.client import Client
from pyrogram.types import (
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
)

from model import InviteLink
from service import channel_open_url, invite_service


@Client.on_chat_join_request()
async def on_chat_join_request(client: Client, request: ChatJoinRequest) -> None:
    """Approve tracked invite join requests and start the membership clock."""
    logger.bind(
        chat_id=request.chat.id if request.chat else None,
        user_id=request.from_user.id if request.from_user else None,
        invite_link=(
            request.invite_link.invite_link if request.invite_link else None
        ),
    ).info("Chat join request received")

    updated = await invite_service.on_join_request(client, request)
    if updated is None:
        return

    logger.bind(
        chat_id=request.chat.id if request.chat else None,
        user_id=updated.joined_user_id,
        link_id=str(updated.id),
    ).info("Join request handled; invite active")

    if updated.joined_user_id is not None:
        await _send_welcome_dm(client, updated.joined_user_id, updated)


async def _send_welcome_dm(client: Client, user_id: int, invite: InviteLink) -> None:
    """DM the member a welcome note with a button back to the channel invite."""
    await client.send_message(
        user_id,
        "👋 Welcome!\n\n"
        f"Your request to join {invite.channel_title} was approved.\n\n"
        "Tap below to open the channel.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 Get back to channel",
                        url=channel_open_url(invite.channel_id),
                    )
                ]
            ]
        ),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
