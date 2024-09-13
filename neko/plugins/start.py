from pyrogram import filters

from neko.core.messages import Message
from neko.neko import Client


@Client.on_message(filters.command('start'))
async def start_handler(_, m: Message):
    return await m.reply_msg(
        'Hallo World!',
    )
