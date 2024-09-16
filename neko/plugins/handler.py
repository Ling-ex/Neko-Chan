from pyrogram import enums
from pyrogram import types

from neko.models import members
from neko.neko import Client
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
        if event.from_user.id == user.user.id and not event.new_chat_member:
            return await members.add_user(
                event.chat.id,
                user.user.id,
                user.user.full_name,
                members.Role.LEAVE,
            )
    if event and (user := event.new_chat_member) and not event.old_chat_member:
        return await members.add_user(
            event.chat.id,
            user.user.id,
            user.user.full_name,
        )
