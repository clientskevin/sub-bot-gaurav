from typing import List

from pyrogram import Client, filters
from pyrogram.types import Message, User

from app import configs
from service import add_admin, get_admins, remove_admin


@Client.on_message(
    filters.command("addadmin") & filters.private & filters.user(configs.OWNER_ID)
)
async def addadmin(client: Client, message: Message):
    if len(message.command) != 2:
        admins = await get_admins()
        text = "Admins:\n"
        for admin in admins:
            try:
                user = _get_users(await client.get_users(admin))
                text += f" - {user.mention(style='md')} ({user.id})\n"
            except ValueError:
                text += f" - {admin}\n"
        await message.reply_text(f"Usage: /addadmin <user_id or @username>\n\n{text}")
        return

    raw_user_id = message.text.split(None, 1)[1]
    parsed_user_id: int | str
    if raw_user_id.isdigit():
        parsed_user_id = int(raw_user_id)
    else:
        parsed_user_id = raw_user_id.replace("@", "")

    try:
        user = _get_users(await client.get_users(parsed_user_id))
    except ValueError:
        await message.reply_text("Invalid user id or username")
        return

    added = await add_admin(user.id)
    if added:
        await message.reply_text("Admin added successfully")
    else:
        await message.reply_text("This user is already an admin")


@Client.on_message(
    filters.command("admins") & filters.private & filters.user(configs.OWNER_ID)
)
async def admins(client: Client, message: Message):
    admins = await get_admins()
    text = "Admins:\n"
    for admin in admins:
        try:
            user = _get_users(await client.get_users(admin))
            text += f" - {user.mention(style='md')} ({user.id})\n"
        except ValueError:
            text += f" - {admin}\n"
    await message.reply_text(text)


@Client.on_message(
    filters.command("removeadmin") & filters.private & filters.user(configs.OWNER_ID)
)
async def removeadmin(client: Client, message: Message):
    if len(message.command) != 2:
        admins = await get_admins()
        text = "Admins:\n"
        for admin in admins:
            try:
                user = _get_users(await client.get_users(admin))
                text += f" - {user.mention(style='md')} ({user.id})\n"
            except ValueError:
                text += f" - {admin}\n"
        await message.reply_text(
            f"Usage: /removeadmin <user_id or @username>\n\n{text}"
        )
        return
    raw_user_id = message.text.split(None, 1)[1]
    parsed_user_id: int | str
    if raw_user_id.isdigit():
        parsed_user_id = int(raw_user_id)
    else:
        parsed_user_id = raw_user_id.replace("@", "")

    try:
        user = _get_users(await client.get_users(parsed_user_id))
    except ValueError:
        await message.reply_text("Invalid user id or username")
        return

    removed = await remove_admin(user.id)
    if removed:
        await message.reply_text("Admin removed successfully")
    else:
        await message.reply_text("This user is not an admin")


def _get_users(response: List[User] | User) -> User:
    if isinstance(response, list):
        return response[0]
    return response
