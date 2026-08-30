from contextlib import asynccontextmanager
from loguru import logger

from model.enums import LogTopicEnum
from service.log import log_service


@asynccontextmanager
async def suppress_send_errors(log_msg_prefix: str = None):
    """Context manager to cleanly catch and log errors when sending messages."""
    try:
        yield
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        if log_msg_prefix:
            await log_service.send_log(
                LogTopicEnum.errors, f"🚨 **Delivery Failure**\n\n{log_msg_prefix}: {e}"
            )
