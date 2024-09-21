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
    """
    Sends a reply to a message with specified text.

    Args:
        text (str): The text to send in the reply.
        quote (bool): Whether to quote the original message.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        Message: The sent message object.
    """
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
    """
    Edits the text of a message.

    Args:
        text (str): The new text to set for the message.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        Message: The edited message object.
    """
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
    """
    Deletes a message.

    Args:
        revoke (bool): Whether to revoke the message for all participants.

    Returns:
        bool: True if the message was deleted, False otherwise.
    """
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
    """
    Gets the date of the message adjusted by a timezone offset.

    Returns:
        datetime: The adjusted date and time of the message.
    """
    return self.date + timedelta(hours=7)


Message.reply_msg = reply_text
Message.edit_msg = edit_text
Message.delete_msg = delete
Message.date_jkt = date
