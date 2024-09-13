from pyrogram import filters
from pyrogram import types

from config import Config


def owner_only():
    async def func(_, __, m: types.Message):
        if user := m.from_user:
            if user.id == Config.OWNER:
                return True

        return False

    return filters.create(func, 'FilterOwnerOnly')
