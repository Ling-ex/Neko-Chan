import asyncio
from datetime import timedelta as td
from pyrogram import errors, filters, types
from pyrogram.enums import ChatMemberStatus
from pyrogram.helpers import ikb
from neko.neko import Client
from neko.utils import func, time
from config import Config

async def ensure_user_known(c: Client, chat_id: int, user_id: int):
    try:
        member = await c.get_chat_member(chat_id, user_id)
        return member
    except errors.UserNotParticipant:
        raise ValueError(f"User {user_id} is not in the chat.")
    except errors.PeerIdInvalid:
        raise ValueError(f"User ID {user_id} is not valid.")

async def check_bot_permissions(c: Client, chat_id: int):
    bot_member = await c.get_chat_member(chat_id, 'me')
    if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        raise PermissionError("I'm not an admin or owner in this chat.")
    if bot_member.privileges and not bot_member.privileges.can_restrict_members:
        raise PermissionError("I don't have permission to restrict members.")

async def check_target_admin(c: Client, chat_id: int, user_id: int):
    target_member = await c.get_chat_member(chat_id, user_id)
    if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        raise PermissionError("I can't kick, ban, or mute an admin or owner.")

async def get_group_permissions(chat: types.Chat):
    return chat.permissions or types.ChatPermissions()

@Client.on_message(filters.command(['kick']) & ~filters.private)
@func.require_admin('can_restrict_members')
async def kick_member_handler(c: Client, m: types.Message):
    user_id, reason = await func.user_and_reason(m)
    try:
        await ensure_user_known(c, m.chat.id, int(user_id))
        await check_bot_permissions(c, m.chat.id)
        await check_target_admin(c, m.chat.id, int(user_id))
        user = await c.get_users(int(user_id))
    except (ValueError, PermissionError) as e:
        return await m.reply_msg(str(e))
    except Exception as e:
        return await m.reply_msg(f"Failed to get user: {str(e)}")
    if user.id == c.me.id:
        return await m.reply_msg("I can't kick myself.")
    try:
        await m.chat.ban_member(user.id)
        await m.chat.unban_member(user.id)
        message = f'Kicked {user.mention} (ID: {user.id}) successfully!'
        await m.reply_msg(message)
        await c.send_message(
            chat_id=c.config.CHAT_LOG,
            text=f"Kick: {m.from_user.mention} (ID: {m.from_user.id}) kicked {user.mention} (ID: {user.id})"
        )
    except Exception as e:
        return await m.reply_msg(f"Failed to kick: {str(e)}")

@Client.on_message(filters.command(['ban', 'tban', 'dban', 'unban']) & ~filters.private)
@func.require_admin('can_restrict_members')
async def ban_member_handler(c: Client, m: types.Message):
    command = m.command[0]
    user_id, reason = await func.user_and_reason(m)
    try:
        await ensure_user_known(c, m.chat.id, int(user_id))
        await check_bot_permissions(c, m.chat.id)
        await check_target_admin(c, m.chat.id, int(user_id))
        user = await c.get_users(int(user_id))
    except (ValueError, PermissionError) as e:
        return await m.reply_msg(str(e))
    except Exception as e:
        return await m.reply_msg(f"Failed to get user: {str(e)}")
    if user.id == c.me.id:
        return await m.reply_msg(f"I can't {command} myself.")
    if command == 'unban':
        try:
            await m.chat.unban_member(user.id)
            permissions = await get_group_permissions(m.chat)
            await m.chat.restrict_member(user.id, permissions)
            message = f'Unbanned {user.mention} (ID: {user.id}) successfully!'
            await m.reply_msg(message)
            await c.send_message(
                chat_id=c.config.CHAT_LOG,
                text=f"Unban: {m.from_user.mention} (ID: {m.from_user.id}) unbanned {user.mention} (ID: {user.id})"
            )
        except Exception as e:
            return await m.reply_msg(f"Failed to unban: {str(e)}")
    else:
        time_ban = None
        if command in ['tban', 'dban'] and len(m.command) > 1:
            time_ban = time.format_datetime(m.text.split(None, 1)[1])
        _format = {'user_id': user.id}
        if time_ban:
            _format['until_date'] = time_ban
        try:
            await m.chat.ban_member(**_format)
            message = f'Banned {user.mention} (ID: {user.id}) successfully!'
            await m.reply_msg(
                message,
                reply_markup=ikb([[('UnBanned', f'restrict banned|{user.id}')]])
            )
            await c.send_message(
                chat_id=c.config.CHAT_LOG,
                text=f"Ban: {m.from_user.mention} (ID: {m.from_user.id}) banned {user.mention} (ID: {user.id})"
            )
        except errors.ChatAdminRequired:
            return await m.chat.leave()

@Client.on_message(filters.command(['mute', 'tmute', 'dmute', 'unmute']) & ~filters.private)
@func.require_admin('can_restrict_members')
async def mute_member_handler(c: Client, m: types.Message):
    command = m.command[0]
    user_id, reason = await func.user_and_reason(m)
    try:
        await ensure_user_known(c, m.chat.id, int(user_id))
        await check_bot_permissions(c, m.chat.id)
        await check_target_admin(c, m.chat.id, int(user_id))
        user = await c.get_users(int(user_id))
    except (ValueError, PermissionError) as e:
        return await m.reply_msg(str(e))
    except Exception as e:
        return await m.reply_msg(f"Failed to get user: {str(e)}")
    if user.id == c.me.id:
        return await m.reply_msg(f"I can't {command} myself.")
    if command == 'unmute':
        try:
            permissions = await get_group_permissions(m.chat)
            await m.chat.restrict_member(user.id, permissions)
            message = f'Unmuted {user.mention} (ID: {user.id}) successfully!'
            await m.reply_msg(message)
            await c.send_message(
                chat_id=c.config.CHAT_LOG,
                text=f"Unmute: {m.from_user.mention} (ID: {m.from_user.id}) unmuted {user.mention} (ID: {user.id})"
            )
        except Exception as e:
            return await m.reply_msg(f"Failed to unmute: {str(e)}")
    else:
        time_mute = None
        if command in ['tmute', 'dmute'] and len(m.command) > 1:
            time_mute = time.format_datetime(m.text.split(None, 1)[1])
        _format = {
            'user_id': user.id,
            'permissions': types.ChatPermissions(all_perms=False)
        }
        if time_mute:
            _format['until_date'] = time_mute
        try:
            await m.chat.restrict_member(**_format)
            message = f'Muted {user.mention} (ID: {user.id}) successfully!'
            await m.reply_msg(
                message,
                reply_markup=ikb([[('UnMuted', f'restrict muted|{user.id}')]])
            )
            await c.send_message(
                chat_id=c.config.CHAT_LOG,
                text=f"Mute: {m.from_user.mention} (ID: {m.from_user.id}) muted {user.mention} (ID: {user.id})"
            )
        except errors.ChatAdminRequired:
            return await m.chat.leave()