import asyncio

from pyrogram import enums
from pyrogram import errors
from pyrogram import filters
from pyrogram import types
from pyrogram.helpers import ikb

from neko.neko import Client
from neko.utils.filters import admins_only
from neko.utils.func import require_admin


__MODULE__ = 'Admins'
__HELP__ = """
▎<b>Restrict</b>
- <b>Ban a Member:</b>
  /ban {@/id/reply} {reason}

- <b>Delete the replied message and ban its sender:</b>
  /dban {reply} {reason}

- <b>Ban a Member for specific time:</b>
  /tban {@/id/reply} {time} {reason}

- <b>Unban a Member:</b>
  /unban {@ or ID}

- <b>Kick a Member:</b>
  /kick {@/id/reply}

- <b>Delete the replied message and kick its sender:</b>
  /dkick {@ or ID}


▎<b>Mutes</b>
- <b>Mute a Member:</b>
  /mute {@/id/reply} {reason}

- <b>Delete the replied message and mute its sender:</b>
  /dmute {reply} {reason}

- <b>Mute a Member for specific time:</b>
  /tmute {@/id/reply} {time} {reason}

- <b>Unmute a Member:</b>
  /unmute {@ or ID}


▎<b>Pins</b>
- <b>Pin a message:</b>
  /pin {reply}

- <b>Unpin a message:</b>
  /unpin {reply}

- <b>Pin the message you wrote:</b>
  /permapin {text}

- <b>Remove all pinned messages:</b>
  /unpinall

▎<b>Misc</b>
- <b>Report a Message to Admins</b>
  /report | @admin | @admins


<b>Format Time</b>
- <b>1m</b> = 1 minute
- <b>1h</b> = 1 hour
- <b>1d</b> = 1 day

<blockquote>
<b>Example Usage:</b>
- <b>To restrict a member for 30 minutes:</b>
  <code>/tmute {@/id/reply} 30m {reason}</code>
- <b>To restrict a member for 2 hours:</b>
  <code>/tban {@/id/reply} 2h {reason}</code>
</blockquote>
"""


# Pin Chats
@Client.on_message(
    filters.command([
        'pinned', 'pin',
        'unpin', 'permapin',
        'unpinall',
    ]) & ~filters.private,
)
@require_admin('can_pin_messages')
async def pin_msg_handler(_, m: types.Message):
    if m.command[0] == 'pinned':
        try:
            chat = await _.get_chat(m.chat.id)
        except Exception:
            pass
        pinned = chat.pinned_message.id
        text_pinned = (
            'https://t.me/c/'
            + str(m.chat.id).replace('-100', '')
            + '/'
            + str(pinned)
        )
        return await m.reply_msg(
            '📌 Pinned message',
            reply_markup=ikb(
                [[('👉🏻 Go to messages', text_pinned, 'url')]],
            ),
        )
    elif m.command[0] == 'pin':
        if not (msg := m.reply_to_message):
            return await m.reply_msg(
                'Please reply to the message you want to pin!',
            )
        return await m.reply_msg(
            '<i>Would you like to send a notification pinning this message?.</i>',  # noqa: E501
            reply_to_message_id=msg.id,
            reply_markup=ikb(
                [
                    [
                        ('🔕 No', f'_pinned notnotif|{msg.id}'),
                        ('Yes 🔔', f'_pinned notif|{msg.id}'),
                    ],
                    [
                        ('❌ Cancel', 'cancel_pin pin'),
                    ],
                ],
            ),
        )
    elif m.command[0] == 'unpin':
        if not (msg := m.reply_to_message):
            return await m.reply_msg(
                'Please reply to the message you want to unpin!',
            )
        try:
            await msg.unpin()
        except Exception:
            pass
        return await m.reply_msg(
            '<i>Unpinned Message.</i>',
            reply_to_message_id=msg.id,
            disable_web_page_preview=True,
        )
    elif m.command[0] == 'permapin':
        if len(m.command) < 2:
            return await m.reply_msg(
                'Error pinning message: no message content given',
            )
        text = m.text.split(None, 1)[1]
        msg = await m.reply_msg(text, quote=False)
        try:
            await msg.pin()
        except Exception:
            pass
        return await m.reply_msg(
            '<i>Pinned messages.</i>',
            reply_to_message_id=msg.id,
        )
    else:
        return await m.reply_msg(
            f'Are you sure you want to delete all the embeds {m.chat.title}?',
            reply_markup=ikb(
                [
                    [
                        ('❌ NO', 'cancel_pin unpinall'),
                        ('✅ Yes', '_pinned unpinall|0'),
                    ],
                ],
            ),
        )


@Client.on_callback_query(filters.regex(r'^_pinned'))
@require_admin('can_pin_messages')
async def cb_pinned_handler(c: Client, cb: types.CallbackQuery):
    try:
        await cb.answer()
    except errors.QueryIdInvalid:
        pass
    await cb.message.delete_msg()
    tipe, msg_id = cb.data.strip().split(None, 1)[1].split('|')
    chat_id = cb.message.chat.id
    msg_id = int(msg_id)
    if tipe == 'notif':
        try:
            await c.pin_chat_message(
                chat_id,
                msg_id,
                disable_notification=True,
            )
        except Exception as e:
            return await cb.message.reply_msg(str(e))
        return await cb.message.reply_msg(
            '<i>Pinned Message.</i>',
            reply_to_message_id=msg_id,
        )
    elif tipe == 'notnotif':
        try:
            return await c.pin_chat_message(
                chat_id,
                msg_id,
                disable_notification=False,
            )
        except Exception as e:
            return await cb.message.reply_msg(str(e))
    elif tipe == 'unpinall':
        try:
            member = await c.get_chat_member(chat_id, cb.from_user.id)
        except Exception:  # type: ignore
            return
        if member.status != enums.ChatMemberStatus.OWNER:
            return
        try:
            await c.unpin_all_chat_messages(chat_id)
        except Exception as e:
            return await cb.message.reply_msg(str(e))
        return await cb.message.reply_msg(
            f'<i>successfully uninstalled all embeds in {cb.message.chat.title}</i>',  # noqa: E501
        )


@Client.on_callback_query(filters.regex(r'^cancel_pin'))
@require_admin('can_pin_messages')
async def cb_cancel_pin_msg(_, cb: types.CallbackQuery):
    tipe = cb.data.strip().split(None, 1)[1].strip()
    await cb.answer()
    if tipe == 'pin':
        text = '<i>Pinned Canceled!</i>'
    else:
        text = '<i>Cancels the Unpinall action.</i>'
    return await cb.message.edit_msg(text)


# Report to admin
@Client.on_message(
    filters.group &
    ~filters.bot & ~filters.via_bot
    & filters.text
    & ~admins_only
    & filters.incoming,
)
async def report_admin_handler(c: Client, m: types.Message):
    if m.text.lower().startswith(('@admin', '@admins', '/report')):
        user = m.from_user
        chat = m.chat
        reason = m.text.split(None, 1)[1] if len(m.text.split()) > 1 else None
        text = f"""
<b>⚠️ ATTENTION!</b>
{user.full_name} [<code>{user.id}</code>] requires admin action in Group: <b>{chat.title}</b>"""  # noqa: E501
        if reason is not None:
            text += f'\n\n<b>Reason:</b> \n<blockquote>{reason}</blockquote>'
        admins: list[int] = []
        try:
            members = chat.get_members(
                filter=enums.ChatMembersFilter.ADMINISTRATORS,
            )
        except errors.FloodWait as f:
            await asyncio.sleep(f.value)
            members = chat.get_members()
        async for admin in members:
            if admin.user.is_deleted or admin.user.is_bot:
                continue
            if admin.user.id not in admins:
                admins.append(admin.user.id)
        for user in admins:
            try:
                await c.send_message(
                    user,
                    text,
                    reply_markup=ikb([[('👉🏻 Go to messages', m.link, 'url')]]),
                )
            except (
                errors.PeerIdInvalid,
                errors.InputUserDeactivated,
                errors.UserIsBlocked,
            ):
                continue
            except Exception as e:
                c.log.info(f'admin (report): {str(e)}')
        return await m.reply_msg('Report sent.', quote=False)


@Client.on_message(filters.command('unbanall'))
@require_admin('can_promote_members')
async def unbanall_handler(c: Client, m: types.Message):
    msg = await m.reply_msg(
        '<i>Member Un-Banned process....</i>',
    )
    try:
        get_members = m.chat.get_members(filter=enums.ChatMembersFilter.BANNED)
    except errors.FloodWait as f:
        await asyncio.sleep(f.value)
        get_members = m.chat.get_members(filter=enums.ChatMembersFilter.BANNED)
    done = 0
    async for member in get_members:
        user = member.user
        if user.is_deleted or user.is_bot:
            continue
        try:
            await asyncio.sleep(1)
            await m.chat.unban_member(user.id)
            done += 1
        except errors.FloodWait as f:
            await asyncio.sleep(f.value)
            await m.chat.unban_member(user.id)
            done += 1
        except Exception as e:
            c.log.info(e)
            continue
    if done == 0:
        return await msg.edit_msg(
            'There are no banned users here',
        )
    return await msg.edit_msg(
        'Successfully unlocked all banned on {}.\n\n'
        '<b>Total Un-Banned:</b> <code>{}</code>'.format(m.chat.title, done),
    )


@Client.on_message(filters.command('unmuteall'))
@require_admin('can_promote_members')
async def unmuteall_handler(c: Client, m: types.Message):
    msg = await m.reply_msg(
        '<i>Member Un-Restrict process....</i>',
    )
    try:
        get_members = m.chat.get_members(
            filter=enums.ChatMembersFilter.RESTRICTED,
        )
    except errors.FloodWait as f:
        await asyncio.sleep(f.value)
        get_members = m.chat.get_members(
            filter=enums.ChatMembersFilter.RESTRICTED,
        )
    done = 0
    async for member in get_members:
        user = member.user
        if user.is_deleted or user.is_bot:
            continue
        try:
            await asyncio.sleep(1)
            await m.chat.unban_member(user.id)
            done += 1
        except errors.FloodWait as f:
            await asyncio.sleep(f.value)
            await m.chat.unban_member(user.id)
            done += 1
        except Exception as e:
            c.log.info(e)
            continue

    if done == 0:
        return await msg.edit_msg(
            'There are no user restrictions here',
        )
    return await msg.edit_msg(
        'Successfully unlocked all restricted on {}.\n\n'
        '<b>Total Un-Restricted:</b> <code>{}</code>'.format(
            m.chat.title, done,
        ),
    )


@Client.on_message(filters.command('staff'))
async def staff_group_handler(c: Client, m: types.Message):
    chat = m.chat
    text = f'<b>Staff Group in {chat.title}</b>\n\n'

    try:
        get_members = chat.get_members(
            filter=enums.ChatMembersFilter.ADMINISTRATORS,
        )
    except errors.FloodWait as f:
        await asyncio.sleep(f.value)
        get_members = chat.get_members(
            filter=enums.ChatMembersFilter.ADMINISTRATORS,
        )

    founder = '👑 <b>Founder:</b>\n'
    co_founder = '\n⚜️  <b>Deputy Founder:</b>\n'
    admins = '\n👮🏼 <b>Admins:</b>\n'
    co_founder_list = []
    admins_list = []

    async for staff in get_members:
        user = staff.user
        if user.is_bot or user.is_deleted:
            continue
        mention = '@' + user.username if user.username else user.mention
        if staff.status == enums.ChatMemberStatus.OWNER:
            founder += f' ╰ {mention}\n'
        else:
            if staff.privileges.can_promote_members:
                title = staff.custom_title or None
                co_founder_list.append(
                    f' ├ {mention} » <i>{title}</i>' if title else f' ├ {mention}',  # noqa: E501
                )
            else:
                title = staff.custom_title or None
                admins_list.append(
                    f' ├ {mention} » <i>{title}</i>' if title else f' ├ {mention}',  # noqa: E501
                )

    if co_founder_list:
        co_founder_list[-1] = co_founder_list[-1].replace(' ├', ' ╰')
        co_founder += '\n'.join(co_founder_list) + '\n'
    else:
        co_founder = ''

    if admins_list:
        admins_list[-1] = admins_list[-1].replace(' ├', ' ╰')
        admins += '\n'.join(admins_list) + '\n'
    else:
        admins = ''

    text += founder + co_founder + admins
    return await m.reply_msg(text)
