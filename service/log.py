import sys

from loguru import logger
from pyrogram import Client
from pyrogram.types import Message

from app.config import configs
from app.context import Context
from model.enums import LogTopicEnum

from repository import log_topic_repository


class LogService:
    async def ensure_topics_exist(self, bot: Client):
        log_channel = configs.LOG_CHANNEL
        if not log_channel:
            logger.warning("LOG_CHANNEL is not set. Skipping topic creation.")
            return

        try:
            member = await bot.get_chat_member(log_channel, bot.me.id)
            if not member.privileges or not member.privileges.can_manage_topics:
                logger.error(
                    f"Bot does not have 'Manage Topics' permission in {log_channel}!"
                )
                sys.exit(1)
        except Exception as e:
            logger.error(
                f"Failed to check permissions in LOG_CHANNEL ({log_channel}): {e}"
            )
            sys.exit(1)

        for topic_enum in LogTopicEnum:
            slug = topic_enum.value
            name = slug.capitalize()

            existing = await log_topic_repository.get_topic_by_slug(slug)
            if not existing:
                logger.info(f"Creating missing forum topic: {name}")
                try:
                    topic = await bot.create_forum_topic(
                        chat_id=log_channel, title=name
                    )
                    await log_topic_repository.add_topic(
                        slug=slug, name=name, thread_id=topic.id
                    )
                except Exception as e:
                    logger.error(f"Failed to create topic {name}: {e}")
                    sys.exit(1)

    async def get_thread_id(self, topic: LogTopicEnum) -> int | None:
        record = await log_topic_repository.get_topic_by_slug(topic.value)
        return record.thread_id if record else None

    async def send_log(
        self, topic: LogTopicEnum, text: str, **kwargs
    ) -> Message | None:
        bot = Context.bot
        log_channel = configs.telegram.log_channel
        if not log_channel:
            return None

        thread_id = await self.get_thread_id(topic)
        try:
            return await bot.send_message(
                chat_id=log_channel, text=text, message_thread_id=thread_id, **kwargs
            )
        except Exception as e:
            logger.error(f"Failed to send log to topic {topic.value}: {e}")
            return None


log_service = LogService()
