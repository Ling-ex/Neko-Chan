import contextlib
from typing import Union

from pyrogram import errors
from pyrogram import filters
from pyrogram import types
from pyrogram.helpers import ikb

from neko.enums import AntiSpamType
from neko.models import antispam
from neko.neko import Client
from neko.utils.filters import admins_only


@Client.on_message(
    filters.command('antispam')
    & admins_only
    & ~filters.private,
)
@Client.on_callback_query(filters.regex(r'^bck_antispam') & admins_only)
async def anti_spam_handler(_, m: Union[types.Message, types.CallbackQuery]):
    method = m.message.edit_msg if isinstance(
        m, types.CallbackQuery,
    ) else m.reply_msg
    return await method(
        'Select which Action you want to select below.',
        reply_markup=ikb(
            [
                [
                    ('Anti Forward', 'antispam forward|0'),
                    ('Anti Channel', 'antispam channel|0'),
                ],
                [
                    ('Cancel', 'antispam cancel|0'),
                ],
            ],
        ),
    )


@Client.on_callback_query(filters.regex(r'^antispam') & admins_only)
async def cb_antispam_handler(_, cb: types.CallbackQuery):
    action, what = cb.data.strip().split(None, 1)[1].split('|')

    if action == 'cancel':
        return await cb.message.edit_msg(
            'The action was successfully cancelled.',
        )
    elif action == 'channel':
        type = AntiSpamType.AntiChannel
    elif action == 'forward':
        type = AntiSpamType.AntiForward

    text = f'<b>Set Action for Anti-{action.title()}</b>\n\n'
    data = await antispam.get(cb.message.chat.id, type)
    if (
        what
        and what == '0'
        and data
        and (status := data.status)
    ):
        status = status
    else:
        status = (what == 'yes')
        await antispam.create(
            cb.message.chat.id,
            type,
            status,
        )
    text += f'<b>Status:</b> <code>{status}</code>'
    icon = '✅ Active' if status else '❌ Not active'
    what = 'yes' if not status else 'no'
    with contextlib.suppress(errors.MessageNotModified):
        return await cb.message.edit(
            text,
            reply_markup=ikb(
                [
                    [
                        (icon, f'antispam {action}|{what}'),
                    ],
                    [
                        ('🔙 Back', 'bck_antispam'),
                    ],
                ],
            ),
        )
