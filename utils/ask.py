from pyrogram.types import Message
from app import Context


async def ask(text: str, chat_id: int, **kwargs) -> Message | None:
    try:
        response = await Context.bot.ask(chat_id, text, **kwargs)
    except Exception:
        await Context.bot.send_message(chat_id, "Some error occurred")
        return None
    return response
