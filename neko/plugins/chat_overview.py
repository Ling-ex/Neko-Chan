from pyrogram import filters
from pyrogram import types

from neko.models import members
from neko.neko import Client
from neko.utils import func

__MODULE__ = 'Chat Overview'
__HELP__ = """
▎ <b>Chat Overview</b>
- <b>Add a note about group member changes:</b>
  /add_chat_overview

- <b>Delete a group member change note:</b>
  /del_chat_overview

▎ <b>Function:</b>
<b><i>This feature records updates in the group, including:</i></b>
- Members who join.
- Members who leave.
- Members who are banned.

The change note will be displayed every midnight, with a comparison of the number of group members between yesterday and today."""  # noqa: E501


@Client.on_message(filters.command('add_chat_overview'))
@func.require_admin([])
async def add_chat_overview(c: Client, m: types.Message):
    chat = m.chat
    if await members.get_chat(chat.id):
        return await m.reply_msg(
            'This chat is already in the chat overview.',
        )

    amount = await c.get_chat_members_count(chat.id)
    await members.add_chat(m.chat.id, amount)
    return await m.reply_msg(
        f'Now that chat {chat.title} is in the overview list,'
        'the bot will send an overview notification for this group.',
    )


@Client.on_message(filters.command('del_chat_overview'))
@func.require_admin([])
async def del_chat_overview(c: Client, m: types.Message):
    chat = m.chat
    if not await members.get_chat(chat.id):
        return await m.reply_msg(
            'This chat is not in the overview list.',
        )

    await members.delete_chat(m.chat.id)
    return await m.reply_msg(
        f'{chat.title} successfully removed from overview.',
    )
