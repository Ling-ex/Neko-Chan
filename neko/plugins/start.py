from neko.neko import Client
from neko.core.messages import Message

from pyrogram import filters


@Client.on_message(filters.command("start"))
async def start_handler(_, m: Message):
    return await m.reply_msg(
        "Hallo World!",
    )
