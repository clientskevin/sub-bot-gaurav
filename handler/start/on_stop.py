import pyrogram as pg
from loguru import logger

from app import app_scheduler, close_db


@pg.client.Client.on_stop()
async def on_stop(client: pg.client.Client, *args, **kwargs):
    logger.info("Bot stopping...")
    app_scheduler.shutdown()
    await close_db()
    logger.info("Bot stopped.")
