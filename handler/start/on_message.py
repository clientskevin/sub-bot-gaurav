from pyrogram import ContinuePropagation, StopPropagation, filters
from pyrogram.client import Client
from pyrogram.types import Message

from service import add_user, get_user


@Client.on_message(filters.private & filters.incoming, group=-1)
async def on_message(client: Client, message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await add_user(message.from_user)
    else:
        if user.banned:
            await message.reply("You are banned")
            raise StopPropagation

    raise ContinuePropagation
