from pyrogram import enums
from pyrogram import errors
from pyrogram import filters
from pyrogram import types

from config import Config
from neko.models import members


def _owner():
    """
    Creates a filter that only allows the bot owner to access certain functions.

    Returns:
        Filter: A filter that checks if the message sender is the bot owner.
    """  # noqa: E501
    async def func(_, __, m: types.Message):
        if user := m.from_user:
            if user.id == Config.OWNER:
                return True
        return False

    return filters.create(func, 'FilterOwnerOnly')


def _overview():
    """
    Creates a filter to check if a particular chat is registered or exists in the system.

    Returns:
        Filter: A filter that checks the existence of a chat in the system.
    """  # noqa: E501
    async def func(_, __, m: types.Message):
        if not await members.get_chat(m.chat.id):
            return False
        return True

    return filters.create(func, 'FilterChatOverview')


def _owner_chats():
    """
    Creates a filter that only allows access to chats owned by the owner or channels.

    Returns:
        Filter: A filter that checks if the event is from an owner or channel chat.
    """  # noqa: E501
    async def func(_, __, event: types.Message | types.CallbackQuery):
        if isinstance(event, types.CallbackQuery):
            chat = event.message.chat
        else:
            chat = event.chat
        if chat.type == enums.ChatType.PRIVATE:
            return False
        if chat.type == enums.ChatType.CHANNEL:
            return True
        member = await chat.get_member(event.from_user.id)
        if member.status == enums.ChatMemberStatus.OWNER:
            return True

        return False

    return filters.create(func, 'FilterOwnerGroup')


def _admins_chats():
    """
    Creates a filter that only allows access to messages sent by admins or the owner in a group.

    Returns:
        Filter: A filter that checks if the sender is an admin or the owner in a group.
    """  # noqa: E501
    async def func(_, __, msg: types.Message | types.CallbackQuery):
        m = (
            msg.message
            if isinstance(msg, types.CallbackQuery)
            else msg
        )
        if sender := m.sender_chat:
            return True if sender.id == m.chat.id else False
        try:
            user = await m.chat.get_member(msg.from_user.id)
        except (
            errors.UserNotParticipant,
            errors.PeerIdInvalid,
        ):
            return False

        if (
            user.status
            in (
                enums.ChatMemberStatus.ADMINISTRATOR,
                enums.ChatMemberStatus.OWNER,
            )
        ):
            return True
        return False

    return filters.create(func, 'FilterOnlyAdmins')


owner_only = _owner()
chats_overview = _overview()
owner_chats = _owner_chats()
admins_only = _admins_chats()
