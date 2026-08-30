#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: create.py
Author: Maria Kevin
Created: 2026-08-27
Description: Owner conversation to create a single-use timed invite link.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from loguru import logger
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import CallbackQuery, LinkPreviewOptions, Message

from app import ChannelResolveError, InviteCreateError
from service import invite_service
from utils import ask, check_admin, duration_utils

_CANCEL = "/cancel"
_DURATION_RETRY = (
    "Hmm, I couldn't read that. Just send a number of days — "
    "like 7 for a week, or 1.5 for a day and a half."
)


def _is_cancel(message: Message | None) -> bool:
    if message is None:
        return False
    text = (message.text or message.caption or "").strip().lower()
    return text == _CANCEL


@Client.on_message(filters.command("create") & filters.private & filters.incoming)
@Client.on_callback_query(filters.regex("^create$"))
@check_admin
async def create_invite(bot: Client, update: Message | CallbackQuery) -> None:
    """Start the admin invite-create conversation."""
    if isinstance(update, CallbackQuery):
        if update.message is None:
            return
        await update.answer()
        await run_create_invite_flow(bot, update.message)
        return

    await run_create_invite_flow(bot, update)


async def run_create_invite_flow(bot: Client, message: Message) -> None:
    """Ask for channel and duration, then create and send a single-use invite."""
    chat_id = message.chat.id
    owner_id = message.from_user.id
    logger.bind(owner_id=owner_id).info("Starting invite create flow")

    channel_id: int | None = None
    channel_title: str | None = None

    while True:
        response = await ask(
            "Which channel is this invite for?\n\n"
            "You can forward any post from it, or just send the "
            "@username / chat id.\n\n"
            "Changed your mind? Send /cancel anytime.",
            chat_id,
        )
        if response is None:
            return
        if _is_cancel(response):
            await bot.send_message(chat_id, "❌ Cancelled\n\nInvite creation aborted.")
            return

        try:
            channel_id, channel_title = await invite_service.resolve_channel(
                bot, response
            )
        except ChannelResolveError as e:
            await bot.send_message(chat_id, e.user_message)
            continue

        rights_msg = await invite_service.ensure_bot_rights(bot, channel_id)
        if rights_msg is not None:
            await bot.send_message(chat_id, rights_msg)
            continue
        break

    assert channel_id is not None and channel_title is not None

    while True:
        response = await ask(
            f"Nice — got {channel_title}.\n\n"
            "How many days should they keep access after joining?\n"
            "For example: 7 for a week, or 1.5 for a day and a half.\n\n"
            "Send /cancel if you want to stop.",
            chat_id,
        )
        if response is None:
            return
        if _is_cancel(response):
            await bot.send_message(chat_id, "❌ Cancelled\n\nInvite creation aborted.")
            return

        parsed = duration_utils.parse_days_float(
            (response.text or response.caption or "").strip()
        )
        if parsed is None:
            await bot.send_message(chat_id, _DURATION_RETRY)
            continue
        break

    try:
        doc = await invite_service.create_invite(
            bot,
            channel_id=channel_id,
            duration_seconds=parsed.duration_seconds,
            created_by=owner_id,
        )
    except InviteCreateError as e:
        await bot.send_message(chat_id, e.user_message)
        return

    await bot.send_message(
        chat_id,
        "✅ Invite Ready\n\n"
        f"Channel: {channel_title}\n"
        f"Access lasts {parsed.breakdown}.\n\n"
        "Single-use invite link:\n"
        f"`{doc.invite_link}`",
        link_preview_options=LinkPreviewOptions(
            is_disabled=True,
        ),
    )
    logger.bind(
        owner_id=owner_id,
        channel_id=channel_id,
        link_id=str(doc.id),
        duration_seconds=parsed.duration_seconds,
    ).info("Invite create flow completed")
