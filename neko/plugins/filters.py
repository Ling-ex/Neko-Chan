from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from neko.models.filters import add_filter, get_filter, get_all_filters, delete_filter, delete_all_filters
from neko.neko import Client
from neko.utils import func
from config import Config
from neko.utils.filters import admins_only

chat_log = Config.CHAT_LOG

@Client.on_message(filters.command("filters") & filters.group & admins_only)
async def view_filters(client: Client, m: Message):
    filters_list = await get_all_filters(m.chat.id)
    if not filters_list:
        await m.reply_text("No filters are active in this chat.")
        return

    filters_text = "\n".join([f"• <code>{f.keyword}</code>" for f in filters_list])
    await m.reply_text(f"Active filters:\n{filters_text}", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["filter", "addfilter"]) & filters.group & admins_only)
async def add_filter_command(client: Client, m: Message):
    if len(m.command) < 2:
        await m.reply_text("Usage: /filter <keyword> <reply_message> or reply to a message with /filter <keyword>")
        return

    keyword = m.command[1].lower()
    
    if m.reply_to_message:
        if m.reply_to_message.text:
            reply_text = m.reply_to_message.text
        else:
            await m.reply_text("You must reply to a text message.")
            return
    else:
        reply_text = " ".join(m.command[2:])
    
    await add_filter(m.chat.id, keyword, reply_text)

    if chat_log != 0 and chat_log is not None:
        await client.send_message(
            chat_log,
            f"Filter '<code>{keyword}</code>' has been added in <b>{m.chat.title}</b>.",
            parse_mode=enums.ParseMode.HTML
        )
    
    await m.reply_text(f"Filter '<code>{keyword}</code>' has been set.", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command("unfilter") & filters.group & admins_only)
async def remove_filter_command(client: Client, m: Message):
    if len(m.command) < 2:
        await m.reply_text("Usage: /unfilter <keyword>")
        return

    keyword = m.command[1].lower()
    if await delete_filter(m.chat.id, keyword):
        if chat_log != 0 and chat_log is not None:
            await client.send_message(
                chat_log,
                f"Filter '<code>{keyword}</code>' has been removed from <b>{m.chat.title}</b>.",
                parse_mode=enums.ParseMode.HTML
            )
        await m.reply_text(f"Filter '<code>{keyword}</code>' has been removed.", parse_mode=enums.ParseMode.HTML)
    else:
        await m.reply_text(f"No such filter '<code>{keyword}</code>' exists.", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command("removeallfilters") & filters.group & admins_only)
async def remove_all_filters_command(client: Client, m: Message):
    await delete_all_filters(m.chat.id)
    if chat_log != 0 and chat_log is not None:
        await client.send_message(
            chat_log,
            f"All filters have been removed from <b>{m.chat.title}</b>.",
            parse_mode=enums.ParseMode.HTML
        )
    await m.reply_text("All filters have been removed.", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.text & filters.group, group=1)
async def filter_watcher(client: Client, m: Message):
    filters_list = await get_all_filters(m.chat.id)
    message_text = m.text.lower()

    for f in filters_list:
        if re.search(rf"\b{re.escape(f.keyword)}\b", message_text):
            reply = replace_placeholders(f.reply_text, m)

            if "[button:" in reply:
                try:
                    reply_content, button_section = reply.split("[button:", 1)
                    buttons = parse_buttons(button_section)

                    await m.reply_text(
                        reply_content.strip(),
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=buttons
                    )
                except ValueError:
                    await m.reply_text("Error: Invalid button format.", parse_mode=enums.ParseMode.HTML)
            else:
                await m.reply_text(reply, parse_mode=enums.ParseMode.HTML)
            break

def replace_placeholders(reply, m):
    user_first = m.from_user.first_name
    user_username = f"@{m.from_user.username}" if m.from_user.username else "N/A"
    user_id = m.from_user.id
    user_mention = f"<a href='tg://user?id={user_id}'>{user_first}</a>"
    chat_name = m.chat.title or "this chat"

    return (
        reply.replace("{first}", user_first)
             .replace("{username}", user_username)
             .replace("{id}", str(user_id))
             .replace("{mention}", user_mention)
             .replace("{chatname}", chat_name)
    )

def parse_buttons(button_section):
    button_lines = button_section.rstrip("]").split(";")
    keyboard = []

    for line in button_lines:
        buttons = [
            InlineKeyboardButton(text.strip(), url=url.strip())
            for text, url in [btn.split(",", 1) for btn in line.split("|")]
        ]
        keyboard.append(buttons)

    return InlineKeyboardMarkup(keyboard)