import asyncio
import typing
from datetime import datetime
from datetime import timedelta

from pyrogram import errors
from pyrogram.types import Message


async def reply_text(
    self: Message,
    text: str,
    quote: bool = True,
    *args,
    **kwargs: typing.Any,
) -> 'Message':
    try:
        msg = await self.reply_text(
            text=text,
            quote=quote,
            *args,
            **kwargs,
        )
        return msg
    except (
        errors.FloodWait,
        errors.SlowmodeWait,
    ) as fs:
        await asyncio.sleep(fs.value)
        return await self.reply_text(
            text=text,
            quote=quote,
            *args,
            **kwargs,
        )
    except (
        errors.TopicClosed,
        errors.ChatWriteForbidden,
        errors.ChatAdminRequired,
        errors.ChatSendPlainForbidden,
    ):
        return self.stop_propagation()


async def edit_text(
    self: Message, text: str, *args, **kwargs: typing.Any,
) -> 'Message':
    try:
        msg = await self.edit_text(
            text=text, *args, **kwargs,
        )
        return msg
    except errors.FloodWait as f:
        await asyncio.sleep(f.value)
        return await self.edit_text(text=text, *args, **kwargs)
    except (
        errors.ChatWriteForbidden,
        errors.ChatAdminRequired,
        errors.ChatSendPlainForbidden,
        errors.MessageNotModified,
    ):
        return self.stop_propagation()


async def delete(
    self: Message, revoke: bool = True,
) -> bool:
    try:
        msg = await self.delete(revoke=revoke)
        return bool(msg)
    except errors.FloodWait as f:
        await asyncio.sleep(f.value)
        return bool(await self.delete(revoke=revoke))
    except errors.MessageDeleteForbidden:
        return False


@property  # type: ignore
def date(self: Message) -> datetime:
    return self.date + timedelta(hours=7)


Message.reply_msg = reply_text
Message.edit_msg = edit_text
Message.delete_msg = delete
Message.date_jkt = date
