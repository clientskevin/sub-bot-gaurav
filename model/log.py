from beanie import Document, Indexed


class LogTopic(Document):
    slug: Indexed(str, unique=True)
    name: str
    thread_id: int

    class Settings:
        name = "log_topics"
