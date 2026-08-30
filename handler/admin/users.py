from pyrogram import Client, filters, types

from repository import user_repository
from utils import check_admin


@Client.on_message(filters.command("users", prefixes="/") & filters.incoming)
@Client.on_callback_query(filters.regex(pattern=r"^users"))
@check_admin
async def users(client, message):
    page = 1
    if isinstance(message, types.CallbackQuery):
        if len(message.data.split()) == 2:
            page = int(message.data.split()[1])

    per_page = 20  # Number of users per page
    skip = (page - 1) * per_page
    users_list = await user_repository.get_users(skip=skip, limit=per_page)
    total_users_count = await user_repository.get_users_count()

    if users_list:
        user_ids = [user.id for user in users_list]
        paginated_users = await client.get_users(user_ids, raise_error=False)

        if not isinstance(paginated_users, list):
            paginated_users = [paginated_users]

        users = ""
        for user in paginated_users:
            if isinstance(user, types.User):
                users += f"👤 `{user.id}` - {user.mention}\n"
            else:
                users += f"🚫 `{user}` - Blocked Account\n"

        # Calculate the number of pages
        total_pages = (total_users_count + per_page - 1) // per_page

        # Generate pagination buttons
        buttons = []
        if page > 1:
            buttons.append(
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"users {page - 1}")
            )
        if page < total_pages:
            buttons.append(
                types.InlineKeyboardButton("➡️ Next", callback_data=f"users {page + 1}")
            )
        buttons.append(
            types.InlineKeyboardButton(f"Page {page}/{total_pages}", callback_data="1")
        )
        buttons = [buttons]
        buttons.append([types.InlineKeyboardButton("🔙 Back", callback_data="admin")])

        # Create inline keyboard markup
        keyboard = types.InlineKeyboardMarkup(buttons)
        func = (
            message.edit_message_text
            if isinstance(message, types.CallbackQuery)
            else message.reply_text
        )
        await func(
            f"**Total Users:**\n\n{users}\n**Total Users Count:** {total_users_count}",
            reply_markup=keyboard,
        )

    else:
        await message.reply_text("**Total Users:**\n\nNo Users")
