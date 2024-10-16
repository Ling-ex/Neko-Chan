import re
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, RPCError
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import ChatMemberUpdated

from neko.neko import Client
from config import Config
from neko.utils.filters import admins_only
from neko.models.greetings_db import GreetingSettings, get_greeting_settings, update_greeting_settings

CHAT_LOG = Config.CHAT_LOG


def replace_placeholders(text, user, chat):
    return text.replace("{first}", user.first_name)\
               .replace("{username}", f"@{user.username}" if user.username else "N/A")\
               .replace("{id}", str(user.id))\
               .replace("{chatname}", chat.title or "this chat")


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


@Client.on_chat_member_updated(filters.group)
async def member_has_joined(client: Client, member: ChatMemberUpdated):
    if (
        member.new_chat_member
        and member.new_chat_member.status not in {CMS.BANNED, CMS.LEFT, CMS.RESTRICTED}
        and not member.old_chat_member
    ):
        user = member.new_chat_member.user
        chat_id = member.chat.id

        settings = await get_greeting_settings(chat_id)
        if not settings or settings.welcome_off:
            return

        custom_welcome = settings.welcome_message
        welcome_text = replace_placeholders(custom_welcome.strip(), user, member.chat)
        
        if custom_welcome:
            welcome_message = await client.send_message(chat_id, welcome_text)
        else:
            welcome_text = f"Welcome {user.mention} to {member.chat.title}!"
            welcome_message = await client.send_message(chat_id, welcome_text)

        if settings.cleanwelcome_on:
            old_welcome = settings.last_welcome
            if old_welcome:
                try:
                    await client.delete_messages(chat_id, old_welcome)
                except (ChatAdminRequired, RPCError):
                    pass
            settings.last_welcome = welcome_message.id
            await update_greeting_settings(chat_id, settings.dict())


# Sementara tidak aktif (Not active yet)
# @Client.on_chat_member_updated(filters.group)
# async def member_has_left(client: Client, member: ChatMemberUpdated):
#     if (
#         not member.new_chat_member
#         and member.old_chat_member.status not in {CMS.BANNED, CMS.RESTRICTED}
#         and member.old_chat_member
#     ):
#         user = member.old_chat_member.user
#         chat_id = member.chat.id

#         settings = await get_greeting_settings(chat_id)
#         if not settings or settings.goodbye_off:
#             return

#         custom_goodbye = settings.goodbye_message
#         goodbye_text = replace_placeholders(custom_goodbye.strip(), user, member.chat)

#         if custom_goodbye:
#             goodbye_message = await client.send_message(chat_id, goodbye_text)
#         else:
#             goodbye_text = f"Goodbye {user.mention}!"
#             goodbye_message = await client.send_message(chat_id, goodbye_text)

#         if settings.cleangoodbye_on:
#             old_goodbye = settings.last_goodbye
#             if old_goodbye:
#                 try:
#                     await client.delete_messages(chat_id, old_goodbye)
#                 except (ChatAdminRequired, RPCError):
#                     pass
#             settings.last_goodbye = goodbye_message.id
#             await update_greeting_settings(chat_id, settings.dict())


@Client.on_message(filters.command("setwelcome") & filters.group & admins_only)
async def set_welcome_message(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /setwelcome <welcome_message>")
        return

    custom_welcome = " ".join(message.command[1:])
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.welcome_message = custom_welcome
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Custom welcome message has been set.")


@Client.on_message(filters.command("setgoodbye") & filters.group & admins_only)
async def set_goodbye_message(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /setgoodbye <goodbye_message>")
        return

    custom_goodbye = " ".join(message.command[1:])
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.goodbye_message = custom_goodbye
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Custom goodbye message has been set.")


@Client.on_message(filters.command("welcome_on") & filters.group & admins_only)
async def welcome_on(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.welcome_off = False
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Welcome messages are now enabled.")


@Client.on_message(filters.command("welcome_off") & filters.group & admins_only)
async def welcome_off(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.welcome_off = True
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Welcome messages are now disabled.")


@Client.on_message(filters.command("goodbye_on") & filters.group & admins_only)
async def goodbye_on(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.goodbye_off = False
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Goodbye messages are now enabled.")


@Client.on_message(filters.command("goodbye_off") & filters.group & admins_only)
async def goodbye_off(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.goodbye_off = True
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Goodbye messages are now disabled.")


@Client.on_message(filters.command("cleanwelcome_on") & filters.group & admins_only)
async def clean_welcome_on(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.cleanwelcome_on = True
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Clean welcome is now enabled.")


@Client.on_message(filters.command("cleanwelcome_off") & filters.group & admins_only)
async def clean_welcome_off(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.cleanwelcome_on = False
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Clean welcome is now disabled.")


@Client.on_message(filters.command("cleangoodbye_on") & filters.group & admins_only)
async def clean_goodbye_on(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.cleangoodbye_on = True
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Clean goodbye is now enabled.")


@Client.on_message(filters.command("cleangoodbye_off") & filters.group & admins_only)
async def clean_goodbye_off(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.cleangoodbye_on = False
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Clean goodbye is now disabled.")


@Client.on_message(filters.command("cleanservice_on") & filters.group & admins_only)
async def clean_service_on(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.cleanservice_on = True
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Auto clean service messages are now enabled.")


@Client.on_message(filters.command("cleanservice_off") & filters.group & admins_only)
async def clean_service_off(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        settings = GreetingSettings(chat_id=chat_id)

    settings.cleanservice_on = False
    await update_greeting_settings(chat_id, settings.dict())
    await message.reply_text("Auto clean service messages are now disabled.")


@Client.on_message(filters.command("greetings_settings") & filters.group & admins_only)
async def view_greetings_settings(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_greeting_settings(chat_id)
    if not settings:
        await message.reply_text("No settings found for this group.")
        return

    welcome_status = "✅" if not settings.welcome_off else "❌"
    goodbye_status = "✅" if not settings.goodbye_off else "❌"
    cleanwelcome_status = "✅" if settings.cleanwelcome_on else "❌"
    cleangoodbye_status = "✅" if settings.cleangoodbye_on else "❌"
    cleanservice_status = "✅" if settings.cleanservice_on else "❌"

    await message.reply_text(
        f"Greetings Settings for {message.chat.title}:\n"
        f"Welcome: {welcome_status}\n"
        f"Goodbye: {goodbye_status}\n"
        f"Clean Welcome: {cleanwelcome_status}\n"
        f"Clean Goodbye: {cleangoodbye_status}\n"
        f"Auto Clean Service Messages: {cleanservice_status}",
        parse_mode=enums.ParseMode.HTML
    )
