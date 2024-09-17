from math import ceil
from typing import List
from typing import Tuple

from pyrogram import enums
from pyrogram.types import InlineKeyboardButton


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(
    page_n: int,
    module_dict: dict,
    prefix: str,
    chat: enums.ChatType,
) -> List[
    Tuple[
        EqInlineKeyboardButton,
        EqInlineKeyboardButton,
        EqInlineKeyboardButton,
    ]
]:
    modules = sorted([
        EqInlineKeyboardButton(
            x.__MODULE__,
            callback_data='{}_module({})'.format(
                prefix, x.__MODULE__.replace(' ', '_').lower(),
            ),
        )
        for x in module_dict.values()
    ])
    line = 4
    pairs = list(zip(modules[::3], modules[1::3], modules[2::3]))
    i = 0
    for m in pairs:
        for _ in m:
            i += 1
    if len(modules) - i == 1:
        pairs.append(
            (
                modules[-1], EqInlineKeyboardButton('', ''),
                EqInlineKeyboardButton('', ''),
            ),
        )
    elif len(modules) - i == 2:
        pairs.append((
            modules[-2], modules[-1],
            EqInlineKeyboardButton('', ''),
        ))

    max_num_pages = ceil(len(pairs) / line)
    modulo_page = page_n % max_num_pages

    buttons = pairs[modulo_page * line: line * (modulo_page + 1)]
    # if use in bot: add home button
    if chat == enums.ChatType.PRIVATE:
        home_button = EqInlineKeyboardButton(
            'Home',
            callback_data='home',
        )
        buttons.append((
            home_button, EqInlineKeyboardButton(
                '', '',
            ), EqInlineKeyboardButton('', ''),
        ))

    if len(pairs) > line:
        buttons.append((
            EqInlineKeyboardButton(
                '«',
                callback_data=f'{prefix}_prev({modulo_page})',
            ),
            EqInlineKeyboardButton(
                '»',
                callback_data=f'{prefix}_next({modulo_page})',
            ),
            EqInlineKeyboardButton('', ''),
        ))

    return buttons
