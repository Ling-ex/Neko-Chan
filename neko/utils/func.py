import re
from functools import partial
from functools import wraps
from typing import Any
from typing import Callable
from typing import Optional
from typing import Tuple

from pyrogram import Client
from pyrogram import enums
from pyrogram import errors
from pyrogram import types


async def check_perms(
    m: types.Message | types.CallbackQuery, permissions: str | list[str],
) -> bool:
    """
    Checks if the user has the required admin permissions.

    Parameters:
        m (types.Message | types.CallbackQuery):
            The message or callback query object to be checked.
        permissions (str | list[str]):
            The permission or list of permissions
            the user must have.

    Returns:
        bool: True if the user is an admin with the required
            permissions, False otherwise.
    """

    if isinstance(m, types.CallbackQuery):
        method = partial(m.answer, show_alert=True)
        chat = m.message.chat
    else:
        method = m.reply_msg
        chat = m.chat
    try:
        user = await chat.get_member(m.from_user.id)
    except (
        errors.UserNotParticipant,
        errors.PeerIdInvalid,
        AttributeError,
    ):
        return False
    if user.status == enums.ChatMemberStatus.OWNER:
        return True
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR:
        await method(
            (
                'You cannot perform this action because '
                'you are not an administrator.'
            ),
        )
        return False
    if (
        not permissions
        and user.status == enums.ChatMemberStatus.ADMINISTRATOR
    ):
        return True
    missing_perms = [
        permission
        for permission in (
            [permissions]
            if isinstance(permissions, str)
            else permissions
        )
        if not getattr(user.privileges, permission)
    ]

    if not missing_perms:
        return True
    await method(
        (
            'You lack permission to use the following command: '
            '{permissions}'
        ).format(
            permissions=', '.join(
                perm.replace('_', ' ').title().replace(
                    ' ', '',
                ) for perm in missing_perms
            ),
        ),
    )

    return False


def require_admin(permissions: str | list[str]) -> Callable:
    """
    Decorator to ensure that the user has the required admin permissions.

    Parameters:
        permissions (str | list[str]):
            The permission or list of permissions needed
            by the admin.

    Returns:
        Callable: A decorator that wraps the function to
            include admin permission checks.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            self: Client,
            msg: types.Message | types.CallbackQuery,
            *args,
            **kwargs: Any,
        ):
            event = msg.message if isinstance(
                msg, types.CallbackQuery,
            ) else msg
            if event.chat.type == enums.ChatType.CHANNEL:
                return await func(self, msg, *args, **kwargs)

            if (
                not msg.from_user
                and msg.sender_chat
                and msg.sender_chat.id == msg.chat.id
            ):
                return await func(self, msg, *args, **kwargs)

            # Check for required permissions and proceed if the user has them.
            if await check_perms(msg, permissions):
                return await func(self, msg, *args, **kwargs)

        return wrapper

    return decorator


async def extract_userid(msg, text: str) -> Optional[int]:
    """
    Extracts the user ID from a message based on text or entity.

    Parameters:
        msg: The message object containing potential user information.
        text (str): The text from which the user ID might be extracted.

    Returns:
        Optional[int]: The extracted user ID, or None if not found.
    """

    args = text.strip()
    entities = msg.entities
    app = msg._client
    if len(entities) < 2:
        return (await app.get_users(args)).id
    if entity := entities[1]:
        if entity.type == enums.MessageEntityType.MENTION:
            return (await app.get_users(args)).id
        elif entity.type == enums.MessageEntityType.TEXT_MENTION:
            return entity.user.id
        else:
            return None

    return None


async def user_and_reason(
    msg: types.Message,
) -> Tuple[Optional[int], Optional[str]]:
    """
    Extracts the user ID and reason from a message.

    Parameters:
        msg (Message): The message object from which to extract information.

    Returns:
        Tuple[Optional[int], Optional[str]]:
            A tuple containing the user ID and reason,
            or None if not found.
    """

    text = msg.text
    args = text.strip().split()
    user, reason = None, None
    if rep := msg.reply_to_message:
        if user := rep.from_user:
            user = user.id
        elif rep.sender_chat and rep.sender_chat.id != msg.chat.id:
            user = rep.sender_chat.id
        else:
            return None, None
        reason = None if len(args) < 2 else text.split(None, 1)[1]
        if reason is not None:
            reason = re.sub(r'([0-9]+)([dhms])', '', reason.lower()).strip()
        return user, reason

    if len(args) == 2:
        user = text.split(None, 1)[1]
        if user.isdigit():
            return user, None
        return await extract_userid(msg, user), None
    if len(args) > 2:
        user, reason = text.split(None, 2)[1:]
        reason = re.sub(r'([0-9]+)([dhms])', '', reason.lower()).strip()
        return await extract_userid(msg, user), reason

    return user, reason
