import asyncio

from pyrogram import errors
from pyrogram import filters
from pyrogram import types
from pyrogram import enums
from pyrogram.helpers import ikb

from neko.neko import Client
from neko.utils.func import require_admin



def admins_only():
    async def func(_, c: Client, msg: types.Message | types.CallbackQuery):
        m = msg.message if isinstance(msg, types.CallbackQuery) else msg
        if sender := m.sender_chat:
            return True if sender.id == m.chat.id else False
        try:
            user = await m.chat.get_member(msg.from_user.id)
        except (
            errors.UserNotParticipant,
            errors.PeerIdInvalid,
        ):
            return False

        if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
            return True
        return False

    return filters.create(func, 'FilterOnlyAdmins')


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
            await c.unpin_all_chat_messages(chat_id)
        except Exception as e:
            return await cb.message.reply_msg(str(e))
        return await cb.message.reply_msg(
            '<i>successfully uninstalled all embeds in {cb.message.chat.title}</i>',  # noqa: E501
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
    & ~admins_only()
    & filters.incoming,
    group=99,
)
async def report_admin_handler(c: Client, m: types.Message):
    if m.text.lower().startswith(('@admin', '@admins', '/report')):
        user = m.from_user
        chat = m.chat
        reason = m.text.split(None, 1)[1] if len(m.text.split()) > 1 else None
        text = f"""
<b>⚠️ ATTENTION!</b>
{user.full_name} [<code>{user.id}</code>] requires admin action in Group: <b>{chat.title}</b>"""
        if reason is not None:
            text += f'\n\n<b>Reason:</b> \n<blackquote>{reason}</blackquote>'
        admins: list[int] = []
        try:
            members = chat.get_members()
        except errors.FloodWait as f:
            await asyncio.sleep(f.value)
            members = chat.get_members()
        async for admin in members:
            if admin.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
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
            except errors.PeerIdInvalid:
                continue
            except Exception as e:
                c.logger.info(str(e))
        return await m.reply_msg('Report sent.', quote=False)