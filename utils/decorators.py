import functools
from pyrogram.client import Client
from repository import admin_repository


def check_admin(func):
    """Check if user is admin or not"""

    @functools.wraps(func)
    async def wrapper(client: Client, message):
        chat_id = getattr(message.from_user, "id", None)
        is_admin = await admin_repository.get_admin_by_user_id(chat_id)

        if not is_admin:
            return await client.reply(
                message, "You are not allowed to use this command."
            )
        return await func(client, message)

    return wrapper
