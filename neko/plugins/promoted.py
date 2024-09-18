from typing import Optional

from pyrogram import enums
from pyrogram import errors
from pyrogram import filters
from pyrogram import types
from pyrogram.helpers import ikb

from neko.neko import Client
from neko.utils import func

__MODULE__ = 'Promoted'
__HELP__ = """
▎ <b>Promoting</b>
- <b>Promote a Member</b>
    /admin or /promote {@/ID/reply}

- <b>Demote a Member</b>
    /unadmin or /demote {@/ID/reply}
"""


@Client.on_message(filters.command(['admin', 'promote']))
@func.require_admin('can_promote_members')
async def promote_member_handler(c: Client, m: types.Message):
    user_id: Optional[int | str] = None
    title: Optional[str] = None

    if rep := m.reply_to_message:
        user_id = rep.from_user.id
        if len(m.command) > 1:
            title = (m.text or m.caption).split(None, 1)[1]
    elif len(m.command) > 1:
        user_id = m.text.split()[1] or None
        if len(m.command) > 2:
            title = (m.text or m.caption).split(None, 2)[2]
    if not user_id:
        return await m.reply_msg(
            'User not found.',
        )
    try:
        await c.resolve_peer(user_id)
    except (
        errors.PeerIdInvalid,
        errors.UsernameInvalid,
        errors.UsernameNotOccupied,
    ):
        return await m.reply_msg(
            "I can't find that user.",
        )
    user = await c.get_users(user_id)
    if not (bot := (await m.chat.get_member(c.me.id)).privileges):
        return await m.chat.leave()
    if not bot.can_promote_members:
        return await m.reply_msg(
            "I don't have the right to promote members :D",
        )
    try:
        member = await m.chat.get_member(user.id)
    except errors.UserNotParticipant:
        return await m.reoly_msg(
            'The user is not a member of this chat',
        )
    if member.status == enums.ChatMemberStatus.OWNER:
        return await m.reply_msg(
            f'{member.user.mention} Is the group owner!',
        )
    elif member.status == enums.ChatMemberStatus.ADMINISTRATOR:
        return await m.reply_msg(
            'User already has this role',
        )
    try:
        await m.chat.promote_member(
            user_id=member.user.id,
            privileges=types.ChatPrivileges(
                can_change_info=False,
                can_invite_users=bot.can_invite_users,
                can_delete_messages=bot.can_delete_messages,
                can_restrict_members=bot.can_restrict_members,
                can_pin_messages=bot.can_pin_messages,
                can_promote_members=False,
                can_manage_chat=bot.can_manage_chat,
                can_manage_video_chats=bot.can_manage_video_chats,
            ),
        )
    except errors.RPCError as e:
        return await m.reply_msg(str(e))

    mention = '@' + member.user.username if member.user.username else member.user.mention  # noqa: E501
    text = f'{mention} [ <code>{member.user.id}</code> ] has become 👮🏻‍♂️ Admin.\n'  # noqa: E501
    if title:
        await c.set_administrator_title(
            chat_id=m.chat.id,
            user_id=member.user.id,
            title=title,
        )
        text += f'• <b>Title:</b> {title}'
    return await m.reply_msg(
        text=text,
        reply_markup=ikb([[('🕹 Licensing', f'_promote {member.user.id}')]]),
    )


async def privileges_buttons(user_id: int):
    privileges = user_privileges.get(user_id)
    buttons = []
    for name, value in privileges.items():  # type: ignore
        icon = '✅' if value else '❌'
        buttons.append(
            [(
                f"{icon} {name.replace('_', ' ').title()}",
                f'_promote {user_id}|{name}|{int(not value)}',
            )],
        )
    buttons.append([
        ('✖️ Delete', f'delete_admin {user_id}'),
        ('Save ✔️', f'save_admin {user_id}'),
    ])
    return ikb(buttons)


user_privileges: dict[int, dict[str, bool]] = {}


@Client.on_callback_query(filters.regex('_promote'))
@func.require_admin('can_promote_members')
async def cb_promote_handler(c: Client, cb: types.CallbackQuery):
    data = cb.data.strip().split(None, 1)[1].split('|')
    if len(data) < 2:
        user_id = data[0]
        what = None
        action = None
    else:
        user_id, what, action = data

    user_id = int(user_id)
    if action:
        action = bool(int(action))

    if user_id not in user_privileges:
        if not (bot := (await cb.message.chat.get_member(user_id)).privileges):
            return await cb.message.edit_msg('The user is no longer an admin.')
        user_privileges[user_id] = {
            'can_change_info': bot.can_change_info,
            'can_invite_users': bot.can_invite_users,
            'can_delete_messages': bot.can_delete_messages,
            'can_restrict_members': bot.can_restrict_members,
            'can_pin_messages': bot.can_pin_messages,
            'can_promote_members': bot.can_promote_members,
            'can_manage_chat': bot.can_manage_chat,
            'can_manage_video_chats': bot.can_manage_video_chats,
        }

    if what is not None:
        user_privileges[user_id][what] = action

    try:
        bttn = await privileges_buttons(user_id)
        await cb.message.edit_reply_markup(
            reply_markup=bttn,
        )
    except errors.MessageNotModified:
        pass


@Client.on_callback_query(filters.regex('save_admin'))
@func.require_admin('can_promote_members')
async def is_promote_member(_, cb: types.CallbackQuery):
    user_id = int(cb.data.split()[1])
    try:
        privileges = user_privileges.get(user_id)
        await cb.message.chat.promote_member(
            user_id,
            privileges=types.ChatPrivileges(**privileges),
        )
    except Exception as e:  # type: ignore
        _.log.info(e)
    return await cb.message.edit_reply_markup(
        reply_markup=ikb([[('🕹 Licensing', f'_promote {user_id}')]]),
    )


@Client.on_message(filters.command(['unadmin', 'demote']))
@Client.on_callback_query(filters.regex('delete_admin'))
@func.require_admin('can_promote_members')
async def demote_member_handler(
    c: Client, m: types.Message | types.CallbackQuery,
):
    user_id: Optional[str | int] = None
    if isinstance(m, types.CallbackQuery):
        method = m.message.edit
        user_id = int(m.data.split()[1])
        chat = m.message.chat
    else:
        method = m.reply_msg
        chat = m.chat
        if rep := m.reply_to_message:
            user_id = rep.from_user.id
        elif len(m.command) > 1:
            user_id = m.command[1]
        else:
            return await m.reply_msg(
                'User not found!',
            )
    try:
        await c.resolve_peer(user_id)
    except (
        errors.PeerIdInvalid,
        errors.UsernameInvalid,
        errors.UsernameNotOccupied,
    ):
        return await method(
            "I can't find that user.",
        )
    try:
        user = await c.get_users(user_id)
    except Exception:  # is likely sender_chat
        return await method("I don't know")
    if not (bot := (await chat.get_member(c.me.id)).privileges):
        return await chat.leave()
    if not bot.can_promote_members:
        return await method(
            "I don't have the right to promote members :D",
        )
    try:
        member = await chat.get_member(user.id)
    except errors.UserNotParticipant:
        return await method(
            'The user is not a member of this chat',
        )
    if member.status == enums.ChatMemberStatus.OWNER:
        return await method(
            f'{member.user.mention} Is the group owner!',
        )
    elif member.status != enums.ChatMemberStatus.ADMINISTRATOR:
        return await method(
            'The user is not an admin.',
        )
    await chat.promote_member(
        user_id=user.id,
        privileges=types.ChatPrivileges(
            can_change_info=False,
            can_invite_users=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False,
        ),
    )
    mention = '@' + user.username if user.username else user.mention
    text = f"""
{mention} [ <code>{user.id}</code> ] removed from 👮🏻‍♂️ Admin."""

    return await method(text)
