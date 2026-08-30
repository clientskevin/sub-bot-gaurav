#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: on_startup.py
Author: Maria Kevin
Description: Brief description
"""

import pyrogram as pg
from loguru import logger

from app import Context, app_scheduler, configs, init_db
from service import add_admin, add_user, log_service, set_commands


@pg.client.Client.on_start()
async def on_start(client: pg.client.Client, *args, **kwargs):
    logger.info("Starting bot...")
    await init_db()
    await add_admin(configs.OWNER_ID)

    try:
        client_owner = await client.get_users(configs.OWNER_ID)  # type: ignore
        await add_user(client_owner)
    except Exception as e:
        logger.error(f"Make sure the owner start the bot first: {e}")

    await set_commands(app=client)
    me = await client.get_me()
    logger.info(f"Bot started as {me.username} (ID: {me.id})")

    Context.bot = client
    # await log_service.ensure_topics_exist(client)
    app_scheduler.start(client)
