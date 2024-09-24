from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from . import data


db = data.notes


class Notes(BaseModel):
    """
    Represents a note associated with a chat.

    Attributes:
        chat_id: ID of the chat the note belongs to.
        name: Name of the note.
        value: Text value of the note, if any.
        media: Optional media link associated with the note.
        type: Type of the note, default is 'text'.
    """
    chat_id: int
    name: str
    value: Optional[str] = None
    media: Optional[str] = None
    type: str = Field(default='text')


async def create(
    chat_id: int,
    name: str,
    value: Optional[str],
    media: Optional[str] = None,
    note_type: Optional[str] = None,
) -> bool:
    """
    Creates or updates a note in the database.

    Args:
        chat_id (int): The ID of the chat.
        name (str): The name of the note.
        value (Optional[str]): The content of the note.
        media (Optional[str]): Media associated with the note (optional).
        note_type (Optional[str]): The type of the note (optional).

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    note = Notes(
        chat_id=chat_id,
        name=name,
        value=value,
        media=media,
        type=note_type,
    )
    return await db.update_one(
        {'chat_id': chat_id, 'name': name},
        {'$set': note.dict()},
        upsert=True,
    )


async def get_by_name(
    chat_id: int,
    name: str,
) -> Optional[Notes]:
    """
    Retrieves a note by its name from the specified chat.

    Args:
        chat_id (int): The ID of the chat.
        name (str): The name of the note to retrieve.

    Returns:
        Optional[Notes]: A Notes object if found, or None if not found.
    """
    if data := await db.find_one({'chat_id': chat_id, 'name': name}):
        return Notes(**data)

    return None


async def delete_by_name(
    chat_id: int,
    name: str,
) -> bool:
    """
    Deletes a note by its name from the specified chat.

    Args:
        chat_id (int): The ID of the chat.
        name (str): The name of the note to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    return await db.delete_one({'chat_id': chat_id, 'name': name})


async def get_all_by_chat(chat_id: int) -> List[Notes]:
    """
    Retrieves all notes associated with a specific chat.

    Args:
        chat_id (int): The ID of the chat.

    Returns:
        List[Notes]: A list of Notes objects associated with the chat.
    """
    data = await db.find({'chat_id': chat_id}).to_list(None)

    return [Notes(**doc) for doc in data]
