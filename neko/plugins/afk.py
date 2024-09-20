import re
from datetime import datetime as dt
from typing import Optional

from pyrogram import enums
from pyrogram import filters
from pyrogram import types

from neko.models import afk
from neko.neko import Client
from neko.utils import time
from neko.utils.misc_bttn import dynamic_buttons


@Client.on_message(filters.command('afk'))
async def away_from_keyboard(_, m: types.Message):
    if m.sender_chat:
        return m.stop_propagation()
    if rep := m.reply_to_message:
        reason = (rep.text or rep.caption).html
    elif len(m.command) > 1:
        reason = (m.text or m.caption).html.split(None, 1)[1]
    else:
        reason = None
    await afk.create(m.from_user.id, dt.now(), reason)
    return await m.reply_text(
        'You are now marked as away from keyboard.',
        quote=True,
    )


@Client.on_message(filters.command('noafk'))
async def back_to_keyboard(_, m: types.Message):
    if m.sender_chat:
        return m.stop_propagation()
    user: types.User = m.from_user
    if not (data := await afk.get(user.id)):
        return await m.reply_msg(
            "You didn't go away from the keyboard before.",
        )

    go_away = time.time_since_last_seen(data.last_seen)
    return await m.reply_msg(
        'You are back from being away from the keyboard after'
        f' ({go_away}).',
    )


@Client.on_message(
    filters.group &
    ~filters.bot & ~filters.via_bot
    & filters.incoming,
    group=30,
)
async def go_afk_handler(_, m: types.Message) -> None:
    if m.sender_chat:
        return await m.stop_propagation()
    user_id: Optional[int] = None
    if rep := m.reply_to_message:
        if rep.sender_chat:
            return await m.stop_propagation()
        user_id = (
            rep.from_user.id
            if rep.from_user.id != m.from_user.id
            else None
        )
    if entity := m.entities:
        num = 0
        for _ in range(len(entity)):
            if (entity[num].type) == enums.MessageEntityType.MENTION:
                found = re.findall('@([_0-9a-zA-Z]+)', m.text)
                try:
                    user_id = (await m._client.get_users(found[num])).id
                    if user_id == m.from_user.id:
                        user_id = None
                    if rep and user_id == rep.from_user.id:
                        num += 1
                        continue
                except Exception:
                    num += 1
                    continue
            elif (entity[num].type) == enums.MessageEntityType.TEXT_MENTION:
                user = entity[num].user.id
                if user_id == m.from_user.id:
                    user_id = None
                if rep and user_id == rep.from_user.id:
                    num += 1
                    continue
    if user_id is None:
        return await m.stop_propagation()
    if not (data := await afk.get(user_id)):
        return await m.stop_propagation()
    user = m.from_user
    text = '<b>Away from Keyboard</b>\n'
    button: Optional[types.InlineKeyboardButton] = None

    go_away = time.time_since_last_seen(data.last_seen)
    text += f'    <b>Last Seen:</b> <code>{go_away}</code>\n'
    if reason := data.reason:
        username = '@' + user.username if user.username else 'No Username'
        msg, button = await dynamic_buttons(reason)
        if msg:
            reason = msg.format(
                id=user.id,
                first=user.first_name,
                last=user.last_name,
                fullname=user.full_name,
                mention=user.mention,
                username=username,
                chatname=m.chat.title,
            )
            text += f'    <b>Reason:</b> {reason}\n'
    return await m.reply_msg(
        text,
        disable_web_page_preview=True,
        reply_markup=button,
    )
