import re
from math import ceil
from typing import List
from typing import Optional
from typing import Tuple

from pyrogram import enums
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup


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
    """
    Paginates a given dictionary of modules into a format suitable for inline keyboards.

    Args:
        page_n (int): The current page number to display.
        module_dict (dict): A dictionary of modules to paginate. Each module should have a '__MODULE__' attribute.
        prefix (str): A prefix used in callback data for button interactions.
        chat (enums.ChatType): The type of chat, influencing button layout (e.g., adding a home button for private chats).

    Returns:
        List[Tuple[EqInlineKeyboardButton, EqInlineKeyboardButton, EqInlineKeyboardButton]]:
        A list of tuples, each containing three inline keyboard buttons, representing a page of modules.
    """  # noqa: E501
    # Create sorted list of modules with inline keyboard buttons
    modules = sorted([
        EqInlineKeyboardButton(
            x.__MODULE__,
            callback_data='{}_module({})'.format(
                prefix, x.__MODULE__.replace(' ', '_').lower(),
            ),
        )
        for x in module_dict.values()
    ])

    # Define the number of buttons per line
    line = 4
    # Group modules into pairs of three for the keyboard layout
    pairs = list(zip(modules[::3], modules[1::3], modules[2::3]))
    i = 0

    # Count the number of modules and handle remaining buttons
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

    # Calculate the maximum number of pages
    max_num_pages = ceil(len(pairs) / line)
    # Determine the current page using modulo operation
    modulo_page = page_n % max_num_pages

    # Select the buttons to display on the current page
    buttons = pairs[modulo_page * line: line * (modulo_page + 1)]

    # Add a home button if the chat type is private
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

    # Add navigation buttons if there are multiple pages
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


async def dynamic_buttons(
    text: str,
) -> Tuple[Optional[str], Optional[InlineKeyboardMarkup]]:
    """
    Parses a text string to extract dynamic buttons and returns a message and keyboard markup.

    Args:
        text (str): The input text containing button definitions in a specific format.

    Returns:
        Tuple[Optional[str], Optional[InlineKeyboardMarkup]]:
        A tuple where the first element is the message text (if any), and the second element is the inline keyboard markup.
        Returns (None, None) if the input text is empty.
    """  # noqa: E501

    if len(text) == 0:
        return None, None

    msg = re.split(r'\[.*?\]\(buttonurl:.*?\)', text)[0].strip()

    row: List[InlineKeyboardButton] = []
    keyboard: List[List[InlineKeyboardButton]] = []

    pattern = r'\[(.*?)\]\(buttonurl:(.*?)\)'
    # Iterate over each button found in the text
    for button_name, button_data in re.findall(pattern, text):
        # Check if the button should end the current row
        if button_data.endswith(':same'):

            row.append(
                InlineKeyboardButton(
                    text=button_name,
                    url=button_data[:-5],
                ),
            )
            keyboard.append(row)
            row = []
        else:
            row.append(
                InlineKeyboardButton(
                    text=button_name,
                    url=button_data,
                ),
            )
        # Limit each row to a maximum of 8 buttons
        if len(row) > 8:
            keyboard.append(row)
            row = []

    # Append any remaining buttons to the keyboard
    if len(row) > 0:
        keyboard.append(row)
    button = InlineKeyboardMarkup(keyboard) if keyboard else None

    if len(msg) == 0:
        return None, button

    return msg, button
