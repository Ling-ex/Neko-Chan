from typing import Optional

from pydantic import BaseModel

from . import data
from neko.enums import AntiSpamType
from neko.utils.misc import dict_to_obj

db = data.anti_spam


class ChatStatus(BaseModel):
    chat_id: int
    type: AntiSpamType
    status: bool


async def get(chat_id: int, spam_type: AntiSpamType) -> Optional[ChatStatus]:
    """
    Retrieves the chat status based on the provided chat_id.

    Args:
        chat_id (int): The ID of the chat whose status is to be retrieved.
        spam_type (AntiSpamType): The type of anti-spam.

    Returns:
        Optional[ChatStatus]: A ChatStatus object if found, or None if not found.
    """  # noqa: E501
    data_entry = await db.find_one({'chat_id': chat_id, 'type': spam_type.name})  # noqa: E501
    if data_entry:
        data_obj = dict_to_obj(data_entry)
        data_obj.type = AntiSpamType[data_obj.type]
        return ChatStatus(**vars(data_obj))

    return None


async def create(
    chat_id: int,
    spam_type: AntiSpamType,
    status: bool = True,
) -> bool:
    """
    Creates or updates the chat status in the database.

    Args:
        chat_id (int): The ID of the chat to be created or updated.
        spam_type (AntiSpamType): The type of anti-spam.
        status (bool): The status of the chat (True or False).

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    chat_status = ChatStatus(
        chat_id=chat_id,
        type=spam_type,
        status=status,
    )

    data_entry = chat_status.dict()
    data_obj = dict_to_obj(data_entry)
    data_obj.type = chat_status.type.name

    return await db.update_one(
        {'chat_id': chat_id, 'type': data_obj.type},
        {'$set': vars(data_obj)},
        upsert=True,
    )


async def delete(chat_id: int, spam_type: AntiSpamType) -> bool:
    """
    Deletes the chat status from the database based on the provided chat_id and type.

    Args:
        chat_id (int): The ID of the chat to be deleted.
        spam_type (AntiSpamType): The type of anti-spam to be deleted.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """  # noqa: E501
    return await db.delete_one({
        'chat_id': chat_id,
        'type': spam_type.name,
    })
