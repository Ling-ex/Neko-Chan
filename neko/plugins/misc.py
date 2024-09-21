import re

from pyrogram import enums
from pyrogram import filters
from pyrogram import types

from neko import CMD_HELP
from neko.neko import Client
from neko.utils.misc import get_suggestions
from neko.utils.misc_bttn import paginate_modules


# Text helpers
help_text = '''<b>Need Help?</b>
Click the button below to see a list of available help!'''


# Functions Button Helpers

async def help_parser(
    m: types.Message,
    text: str,
    chat: enums.ChatType,
    keyboard: types.InlineKeyboardMarkup = None,
):
    """
    Parses and sends a help message with an optional inline keyboard.

    Args:
        m (types.Message): The message or callback query to respond to.
        text (str): The help text to be sent.
        chat (enums.ChatType): The type of chat where the message is sent.
        keyboard (types.InlineKeyboardMarkup, optional): Inline keyboard markup for pagination. Defaults to None.

    Returns:
        The result of the message sending or editing method, based on whether the input is a message or callback query.
    """  # noqa: E501
    if not keyboard:
        keyboard = types.InlineKeyboardMarkup(
            paginate_modules(
                0, CMD_HELP, 'help', chat,
            ),
        )
    method = m.message.edit_msg if isinstance(
        m, types.CallbackQuery,
    ) else m.reply_msg
    return await method(
        text, reply_markup=keyboard,
    )


# Handler Command Help
@Client.on_message(filters.command('help'))
async def handle_commands(_, m: types.Message):
    chat = m.chat.type
    if m.command and len(m.command) == 1:
        try:
            return await help_parser(m, help_text, chat)
        except Exception as e:
            _.log.info(str(e))
    else:
        name = (m.text.split(None, 1)[1]).replace(' ', '_').lower()
        if name in CMD_HELP:
            text = f'Help For <b>{CMD_HELP[name].__MODULE__}:</b>\n{CMD_HELP[name].__HELP__}'  # noqa: E501
            return await m.reply_msg(text)
        else:
            valid_cmds = list(CMD_HELP.keys())
            if list_suggest := get_suggestions(name, valid_cmds):
                list_suggest = list(
                    item.replace('_', ' ')
                    for item in list_suggest
                )
                suggestions = ', '.join(list_suggest)
                return await m.reply_msg(f'The command "{name.replace("_", " ")}" is invalid! Did you mean: {suggestions}?')  # noqa: E501
            else:
                return await m.reply_msg(f'The command "{name.replace("_", " ")}" is invalid and no suggestions are available.')  # noqa: E501


# Callbacl Help
@Client.on_callback_query(filters.regex(r'help_(.*?)'))
async def cb_helpers_handler(c: Client, cb: types.CallbackQuery):
    mod_match = re.match(r'help_module\((.+?)\)', cb.data)
    prev_match = re.match(r'help_prev\((\d+)\)', cb.data)
    next_match = re.match(r'help_next\((\d+)\)', cb.data)
    back_match = re.match(r'help_back', cb.data)
    chat = cb.message.chat.type
    if mod_match:
        module = mod_match[1].replace(' ', '_')
        text = (
            f'Help For <b>{CMD_HELP[module].__MODULE__}:</b>\n'
            + CMD_HELP[module].__HELP__
        )
        button = [[
            types.InlineKeyboardButton(
                '« Back', callback_data='help_back',
            ),
        ]]

        await cb.message.edit_msg(
            text=text,
            reply_markup=types.InlineKeyboardMarkup(button),
            disable_web_page_preview=True,
        )

    elif prev_match:
        page = int(prev_match[1]) - 1
        await cb.message.edit_msg(
            text=help_text,
            reply_markup=types.InlineKeyboardMarkup(
                paginate_modules(page, CMD_HELP, 'help', chat),
            ),
            disable_web_page_preview=True,
        )

    elif next_match:
        page = int(next_match[1]) + 1
        await cb.message.edit_msg(
            text=help_text,
            reply_markup=types.InlineKeyboardMarkup(
                paginate_modules(page, CMD_HELP, 'help', chat),
            ),
            disable_web_page_preview=True,
        )

    elif back_match:
        await cb.message.edit_msg(
            text=help_text,
            reply_markup=types.InlineKeyboardMarkup(
                paginate_modules(0, CMD_HELP, 'help', chat),
            ),
            disable_web_page_preview=True,
        )


# Ping
@Client.on_message(filters.command('ping'))
async def ping_handler(_, m: types.Message):
    from time import time
    start = time()
    from pyrogram.raw.functions import Ping
    await _.invoke(Ping(ping_id=_.rnd_id()))
    end = time()
    latency = (end - start) * 1000
    return await m.reply_msg(
        f'<b>Pong!</b>\n<code>{latency:.3f}ms</code>',
    )
