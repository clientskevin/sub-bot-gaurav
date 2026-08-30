#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: start.py
Author: Maria Kevin
Created: 2025-12-13
Description: /start handler and main menu.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
)

from app import configs


def _start_text(user_id: int) -> str:
    if user_id == configs.OWNER_ID:
        return (
            "👋 **Welcome back!**\n\n"
            "Create single-use timed invite links for your channels. "
            "Members are approved automatically and removed when their "
            "access expires.\n\n"
            "Tap **Create Invite** below or send /create to start."
        )
    return (
        "👋 **Welcome!**\n\n"
        "You were added through a timed invite link. When your access period "
        "ends, you'll be removed from the channel automatically.\n\n"
        "Tap **Help** below if you have questions."
    )


def _start_keyboard(user_id: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if user_id == configs.OWNER_ID:
        rows.append([InlineKeyboardButton("🔗 Create Invite", callback_data="create")])
    rows.append([InlineKeyboardButton("❓ Help", callback_data="help")])
    return InlineKeyboardMarkup(rows)


@Client.on_message(filters.command("start") & filters.private & filters.incoming)
@Client.on_callback_query(filters.regex("^start$"))
async def start(bot: Client, update: Message | CallbackQuery):
    user_id = update.from_user.id if update.from_user else None
    if user_id is None:
        return

    await bot.reply(
        update,
        _start_text(user_id),
        reply_markup=_start_keyboard(user_id),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
