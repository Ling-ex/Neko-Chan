from pyrogram import errors
from pyrogram import filters
from pyrogram import types
from pyrogram.helpers import ikb

from neko.neko import Client
from neko.utils import func


# Pin Chats
@Client.on_message(
    filters.command([
        'pinned', 'pin',
        'unpin', 'permapin',
        'unpinall',
    ]) & ~filters.private,
)
@func.require_admin('can_pin_messages')
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
@func.require_admin('can_pin_messages')
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
@func.require_admin('can_pin_messages')
async def cb_cancel_pin_msg(_, cb: types.CallbackQuery):
    tipe = cb.data.strip().split(None, 1)[1].strip()
    await cb.answer()
    if tipe == 'pin':
        text = '<i>Pinned Canceled!</i>'
    else:
        text = '<i>Cancels the Unpinall action.</i>'
    return await cb.message.edit_msg(text)
