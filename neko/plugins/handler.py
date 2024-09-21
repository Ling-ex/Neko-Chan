import asyncio
from typing import Optional

from pyrogram import enums
from pyrogram import errors
from pyrogram import filters
from pyrogram import types

from neko.enums.antispam_type import AntiSpamType
from neko.models import antispam
from neko.models import members
from neko.neko import Client
from neko.utils.filters import admins_only
from neko.utils.filters import chats_overview


@Client.on_chat_member_updated(
    chats_overview,
    group=69,
)
async def handler_update_member(
    c: Client,
    event: types.ChatMemberUpdated,
):
    if event and (user := event.old_chat_member):
        if user.status == enums.ChatMemberStatus.BANNED:
            return await members.add_user(
                event.chat.id,
                user.user.id,
                user.user.full_name,
                members.Role.RESTRICTED,
            )
        if (
            event.from_user.id == user.user.id
            and not event.new_chat_member
        ):
            return await members.add_user(
                event.chat.id,
                user.user.id,
                user.user.full_name,
                members.Role.LEAVE,
            )
    if (
        event
        and (user := event.new_chat_member)
        and not event.old_chat_member
    ):
        return await members.add_user(
            event.chat.id,
            user.user.id,
            user.user.full_name,
        )


def anti_spam():
    async def func(_, __, m: types.Message):
        if not await antispam.db.find_one({'chat_id': m.chat.id}):
            return False
        if (
            m.sender_chat
            or m.forward_from_chat
            or m.forward_date
        ):
            return True

        return False

    return filters.create(func, 'FilterAntiSpam')


@Client.on_message(
    filters.group
    & filters.text
    & ~admins_only
    & anti_spam(),
    group=30,
)
async def handle_anti_channel_and_forward(
    c: Client, m: types.Message,
):
    chat: Optional[types.Chat] = None
    try:
        chat = await c.get_chat(m.chat.id)
    except errors.FloodWait as f:
        await asyncio.sleep(f.value)
        chat = await c.get_chat(m.chat.id)

    linked_chat = chat.linked_chat.id

    type = AntiSpamType
    # Handle anti channel
    if (
        m.sender_chat
        and m.sender_chat.id != m.chat.id
        and m.sender_chat.id != linked_chat
    ):
        if data := await antispam.get(m.chat.id, type.AntiChannel):
            if data.status:
                return await m.delete_msg()

        return m.stop_propagation()

    # Handle anti forward
    if (
        m.forward_from
        and not m.forward_from_chat
        or (
            m.forward_from_chat
            and m.forward_from_chat.id != linked_chat
        )
    ):
        if data := await antispam.get(m.chat.id, type.AntiForward):
            if data.status:
                return await m.delete_msg()

        return m.stop_propagation()
