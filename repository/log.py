from typing import Optional

from model import LogTopic


class LogTopicRepository:
    async def get_topic_by_slug(self, slug: str) -> Optional[LogTopic]:
        """Fetch a log topic by its slug."""
        return await LogTopic.find_one(LogTopic.slug == slug)

    async def add_topic(self, slug: str, name: str, thread_id: int) -> LogTopic:
        """Insert a new log topic document."""
        topic = LogTopic(slug=slug, name=name, thread_id=thread_id)
        await topic.insert()
        return topic


log_topic_repository = LogTopicRepository()
