from pyrogram import filters
from pyrogram import types

from config import Config
from neko.models import members


def _owner():
    async def func(_, __, m: types.Message):
        if user := m.from_user:
            if user.id == Config.OWNER:
                return True

        return False

    return filters.create(func, 'FilterOwnerOnly')


def _overview():
    async def func(_, __, m: types.Message):
        if not await members.get_chat(m.chat.id):
            return False
        return True

    return filters.create(func, 'FilterChatOverview')


owner_only = _owner()
chats_overview = _overview()
