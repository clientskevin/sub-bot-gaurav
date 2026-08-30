from handler.admin.user import user
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from repository import user_repository
from service import get_admins, get_user


@Client.on_callback_query(filters.regex(r"^ban_user"))
async def ban_user(bot: Client, query: CallbackQuery):
    user_id = int(query.data.split()[1])
    _user = await user_repository.get_user_by_user_id(user_id)
    if not _user:
        return await query.answer("No user found with this id!")
    admins = await get_admins()

    if user_id in admins:
        return await query.answer("You can't ban an admin!", show_alert=True)

    if _user.banned:
        await user_repository.unban_user(user_id)
        await query.answer("User unbanned successfully!")
    else:
        await user_repository.ban_user(user_id)
        await query.answer("User banned successfully!")

    await get_user(user_id)

    query.data = f"user {user_id}"
    await user(bot, query)
