from pyrogram import client, types

from app import Context, configs
from repository import user_repository


async def set_commands(app: client.Client):
    COMMANDS = [
        types.BotCommand("start", "Start the app."),
        # broadcast
        types.BotCommand("broadcast", "Broadcast message to all users."),
        types.BotCommand("help", "Need help?"),
    ]
    await app.set_bot_commands(COMMANDS, scope=types.BotCommandScopeAllPrivateChats())


async def add_user(user: types.User):
    _user = await user_repository.get_user_by_user_id(user.id)
    if _user:
        return

    await user_repository.add_user(user.id)
    # await send_start_message(user)
    return True


async def send_start_message(user: types.User):
    client = Context.bot
    chat_id = configs.LOG_CHANNEL

    text = f"New user: {user.mention}"
    await client.send_message(chat_id, text)


async def get_user(user_id: int):
    return await user_repository.get_user_by_user_id(user_id)
