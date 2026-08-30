#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: __main__.py
Author: Maria Kevin
Created: 2025-12-13
Description: Brief description
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


import os

if os.name != "nt":
    import uvloop  # type: ignore

    uvloop.install()


import asyncio
from typing import Iterable, List, Union

import pyromod  # noqa: F401 # pyright: ignore[reportUnusedImport]
from loguru import logger
from pyrogram import errors, raw, types
from pyrogram.client import Client

from .config import configs


class Bot(Client):
    owner: "types.User"

    def __init__(self):
        super().__init__(
            "bot",
            api_id=configs.API_ID,
            api_hash=configs.API_HASH,
            bot_token=configs.BOT_TOKEN,
            plugins=dict[str, str](root="handler"),
        )

    async def get_users(
        self: "Client",
        user_ids: Union[int, str, Iterable[Union[int, str]]],
        raise_error: bool = True,
        limit: int = 200,
    ) -> Union["types.User", List["types.User"]]:
        """Get information about a user.
        You can retrieve up to 200 users at once.

        Parameters:
            user_ids (``int`` | ``str`` | Iterable of ``int`` or ``str``):
                A list of User identifiers (id or username) or a single user id/username.
                For a contact that exists in your Telegram address book you can use his phone number (str).
            raise_error (``bool``, *optional*):
                If ``True``, an error will be raised if a user_id is invalid or not found.
                If ``False``, the function will continue to the next user_id if one is invalid or not found.
            limit (``int``, *optional*):
                The maximum number of users to retrieve per request. Must be a value between 1 and 200.

        Returns:
            :obj:`~pyrogram.types.User` | List of :obj:`~pyrogram.types.User`: In case *user_ids* was not a list,
            a single user is returned, otherwise a list of users is returned.

        Example:
            .. code-block:: python

                # Get information about one user
                await app.get_users("me")

                # Get information about multiple users at once
                await app.get_users([user_id1, user_id2, user_id3])
        """
        is_iterable = not isinstance(user_ids, (int, str))
        if isinstance(user_ids, (str, int)):
            user_ids = [user_ids]
        else:
            user_ids = list(user_ids)

        users = types.List()
        user_ids_chunks = [
            user_ids[i : i + limit] for i in range(0, len(user_ids), limit)
        ]

        # Define the `resolve` function with error handling based on the `raise_error` parameter
        async def resolve(user_id):
            try:
                return await self.resolve_peer(user_id)
            except Exception:
                if raise_error:
                    raise
                else:
                    return user_id

        for chunk in user_ids_chunks:
            chunk_resolved = await asyncio.gather(
                *[resolve(i) for i in chunk if i is not None]
            )

            # Remove any `None` values from the resolved user_ids list
            blocked_accounts = [i for i in chunk_resolved if isinstance(i, int)]
            chunk_resolved = list(filter(None, chunk_resolved))
            chunk_resolved = [i for i in chunk_resolved if not isinstance(i, int)]

            r = await self.invoke(raw.functions.users.GetUsers(id=chunk_resolved))

            for user in await asyncio.gather(
                *[types.User._parse(self, i) for i in r]
            ):
                if user is not None:
                    users.append(user)

            for i in blocked_accounts:
                users.append(i)

        return users if is_iterable else users[0]

    async def reply(self, query, *args, **kwargs):
        if isinstance(query, types.Message):
            return await query.reply(*args, **kwargs)
        elif isinstance(query, types.CallbackQuery):
            return await query.edit_message_text(*args, **kwargs)
        else:
            raise ValueError("Invalid query type")

    async def floodwait_handler(self, func, *args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except errors.FloodWait as e:
            logger.warning(f"Floodwait for {e.value} seconds")
            await asyncio.sleep(e.value)
            return await self.floodwait_handler(func, *args, **kwargs)
