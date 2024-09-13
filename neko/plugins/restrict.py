import asyncio
from datetime import timedelta as td

from pyrogram import errors
from pyrogram import filters
from pyrogram import types
from pyrogram.helpers import ikb

from neko.neko import Client
from neko.utils import func
from neko.utils import time


@Client.on_message(filters.command(['kick', 'dkick']) & ~filters.private)
@func.require_admin('can_restrict_members')
async def kicked_member_handler(c: Client, m: types.Message):
    command = m.command[0]
    lol = f"I can't {command} myself."
    no_user = "I can't find that user."
    user_id, reason = await func.user_and_reason(m)
    if not user_id:
        return await m.reply_msg(no_user)
    if user_id == c.me.id:
        return await m.reply_msg(lol)

    if command == 'dkick' and (rep := m.reply_to_message):
        await asyncio.gather(
            rep.delete(),
            m.delete(),
        )
    try:
        await m.chat.ban_member(user_id)
        await asyncio.sleep(0.5)
        await m.chat.unban_member(user_id)
    except errors.UserAdminInvalid:
        return await m.reply_msg(
            (
                'The action requires admin privileges. '
                'Probably you tried to edit admin privileges '
                "on someone you don't have rights to"
            ),
        )
    except errors.UserAdminInvalid:
        return await m.chat.leave()
    except errors.RPCError as e:
        return await m.reply_msg(str(e))
    action_by = 'Anon' if not m.from_user else m.from_user.mention
    user = await c.get_users(user_id)
    text = f"""
<b>Kicked By:</b> {action_by}
    <b>Kicked User:</b> {user.mention}
"""
    if reason:
        text += f'    <b>Reason:</b> <code>{reason}</code>'
    return await m.reply_msg(text)


@Client.on_message(
    filters.command(
        ['ban', 'dban', 'tban', 'unban'],
    ) & ~filters.private,
)
@func.require_admin('can_restrict_members')
async def ban_member_handler(c: Client, m: types.Message):
    command = m.command[0]
    lol = f"I can't {command} myself."
    no_user = "I can't find that user."
    user_id, reason = await func.user_and_reason(m)

    if not user_id:
        return await m.reply_msg(no_user)
    if user_id == c.me.id:
        return await m.reply_msg(lol)

    time_ban = None
    if command == 'tban' and len(m.command) > 1:
        time_ban = time.format_datetime(m.text.split(None, 1)[1])

    if command == 'unban':
        try:
            await m.chat.unban_member(user_id)
        except errors.ChatAdminRequired:
            return await m.chat.leave()
        except errors.UserAdminInvalid:
            return await m.reply_msg(
                (
                    'The action requires admin privileges. '
                    'Probably you tried to edit admin privileges '
                    "on someone you don't have rights to"
                ),
            )
        except Exception as e:
            c.log.info(f'{command} : {str(e)}')
            return
        user = await c.get_users(user_id)
        return await m.reply_msg(f'Un-Banned {user.mention}')

    if command == 'tban' and time_ban:
        _format = {
            'user_id': user_id,
            'until_date': time_ban,
        }
    else:
        if command == 'dban' and (rep := m.reply_to_message):
            await asyncio.gather(
                rep.delete(),
                m.delete(),
            )
        _format = {'user_id': user_id}

    try:
        await m.chat.ban_member(**_format)
    except errors.ChatAdminRequired:
        return await m.chat.leave()
    except errors.UserAdminInvalid:
        return await m.reply_msg(
            (
                'The action requires admin privileges. '
                'Probably you tried to edit admin privileges '
                "on someone you don't have rights to"
            ),
        )
    except errors.RPCError as e:
        return await m.reply_msg(str(e), quote=True)

    action_by = 'Anon' if not m.from_user else m.from_user.mention
    user = await c.get_users(user_id)
    text = f"""
<b>Banned By:</b> {action_by}
    <b>Banned User:</b> {user.mention}
"""
    if time_ban:
        time_ban = time_ban + td(hours=7)
        text += (
            '    <b>Until:</b> '
            f"<code>{time_ban.strftime('%d/%m/%Y %H:%M')} (UTC+7H)</code>\n"
        )
    if reason:
        text += f'    <b>Reason:</b> <code>{reason}</code>'

    return await m.reply_msg(
        text,
        reply_markup=ikb(
            [[('UnBanned', f'restrict banned|{user.id}')]],
        ),
    )


@Client.on_message(
    filters.command(
        ['mute', 'dmute', 'tmute', 'unmute'],
    ) & ~filters.private,
)
@func.require_admin('can_restrict_members')
async def muted_member_handler(c: Client, m: types.Message):
    command = m.command[0]
    lol = f"I can't {command} myself."
    no_user = "I can't find that user."
    user_id, reason = await func.user_and_reason(m)
    time_mute = None
    if not user_id:
        return await m.reply_msg(no_user)
    if user_id == c.me.id:
        return await m.reply_msg(lol)

    time_mute = None
    if command == 'tmute' and len(m.command) > 1:
        time_mute = time.format_datetime(m.text.split(None, 1)[1])

    if command == 'unmute':
        try:
            await m.chat.restrict_member(
                user_id, types.ChatPermissions(all_perms=True),
            )
        except errors.ChatAdminRequired:
            return await m.chat.leave()
        except errors.UserAdminInvalid:
            return await m.reply_msg(
                (
                    'The action requires admin privileges. '
                    'Probably you tried to edit admin privileges '
                    "on someone you don't have rights to"
                ),
            )
        except Exception as e:
            c.log.info(f'{command} : {str(e)}')
            return
        user = await c.get_users(user_id)
        return await m.reply_msg(f'Un-Muted {user.mention}')
    if command == 'tmute' and time_mute:
        _format = {
            'user_id': user_id,
            'permissions': types.ChatPermissions(all_perms=False),
            'until_date': time_mute,
        }
    else:
        if command == 'dmute' and (rep := m.reply_to_message):
            await asyncio.gather(
                rep.delete,
                m.delete,
            )
        _format = {
            'user_id': user_id,
            'permissions': types.ChatPermissions(all_perms=False),
        }
    try:
        await m.chat.restrict_member(**_format)
    except errors.ChatAdminRequired:
        return await m.chat.leave()
    except errors.UserAdminInvalid:
        return await m.reply_msg(
            (
                'The action requires admin privileges. '
                'Probably you tried to edit admin privileges '
                "on someone you don't have rights to"
            ),
        )
    except errors.RPCError as e:
        return await m.reply_msg(str(e))
    action_by = 'Anon' if not m.from_user else m.from_user.mention
    user = await c.get_users(user_id)
    text = f"""
<b>Muted By:</b> {action_by}
    <b>Muted User:</b> {user.mention}
"""
    if time_mute:
        time_mute = time_mute + td(hours=7)
        text += (
            '    <b>Until:</b> '
            f"<code>{time_mute.strftime('%d-%m-%Y %H:%M')} (UTC+7H)</code>\n"
        )
    if reason:
        text += f'    <b>Reason:</b> <code>{reason}</code>'

    return await m.reply_msg(
        text,
        reply_markup=ikb(
            [[('UnMuted', f'restrict muted|{user.id}')]],
        ),
    )


@Client.on_callback_query(filters.regex(r'^restrict'))
@func.require_admin('can_restrict_members')
async def cb_restricted_member(c: Client, cb: types.CallbackQuery):
    action, user_id = cb.data.strip().split(None, 1)[1].split('|')
    try:
        await cb.message.chat.unban_member(int(user_id))
    except Exception as e:
        return await cb.answer(str(e), show_alert=True)
    return await cb.message.edit_msg(
        '{}\n\n~ <b>User is not {}</b>'.format(
            cb.message.text.html, action.title(),
        ),
    )
