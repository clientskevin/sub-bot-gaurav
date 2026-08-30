from pyrogram import Client, filters
from pyrogram.types import Message

from app import configs


@Client.on_message(
    filters.command("admin") & filters.private & filters.user(configs.OWNER_ID)
)
@Client.on_callback_query(filters.regex("^admin$"))
async def admin(client: Client, message: Message):
    text = (
        "**🛠 Admin Control Panel**\n\n"
        "👤 /addadmin - Add an admin\n"
        "👥 /admins - Get all admins\n"
        "🗑️ /removeadmin - Remove an admin\n"
        "📊 /users - Get all users\n"
        "🔍 /user - User Details, Ban/Unban User\n"
        "📢 /broadcast - Broadcast message to all users"
    )

    await client.reply(message, text)  # type: ignore
    # custom method defined in bot/__init__.py
