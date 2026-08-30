from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
)

from app import configs


def _help_text(user_id: int) -> str:
    lines = [
        "❓ **Help**\n",
        "**For members**",
        "• Open the invite link you received and request to join.",
        "• The bot approves your request and starts your access timer.",
        "• Use the welcome message button to return to the channel.",
        "• When your access expires, you'll be removed automatically.\n",
    ]
    if user_id == configs.OWNER_ID:
        lines.extend(
            [
                "**For you (owner)**",
                "• /create — Start the invite wizard.",
                "• Forward a channel post or send its @username / chat id.",
                "• Set how many days access should last after joining.",
                "• Share the single-use link with one member.",
                "• Send /cancel anytime during /create to abort.\n",
            ]
        )
    lines.extend(
        [
            "**Commands**",
            "/start — Main menu",
            "/help — This message",
        ]
    )
    if user_id == configs.OWNER_ID:
        lines.append("/create — Create a timed invite")
    return "\n".join(lines)


@Client.on_message(filters.command("help") & filters.private & filters.incoming)
@Client.on_callback_query(filters.regex("^help$"))
async def help(bot: Client, update: Message | CallbackQuery):
    user_id = update.from_user.id if update.from_user else None
    if user_id is None:
        return

    await bot.reply(
        update,
        _help_text(user_id),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="start")]]
        ),
    )
