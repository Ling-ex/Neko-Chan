from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from . import data as db
from neko.enums import MemberStatus


# Model for User
class User(BaseModel):
    user_id: int
    name: str
    status: str


# Model for Member
class Member(BaseModel):
    chat_id: int
    chat_count: int = Field(default=0)
    users: List[User] = Field(default_factory=list)


async def get_chat(chat_id: int) -> Optional[Member]:
    """
    Retrieves a Member object based on the chat_id.

    Args:
        chat_id (int): The ID of the chat.

    Returns:
        Optional[Member]: A Member object if found, otherwise None.
    """

    if document := await db.inspections.find_one(
        {'chat_id': chat_id},
    ):
        return Member(**document)

    return None


async def add_chat(chat_id: int, count: int) -> bool:
    """
    Adds or updates the chat count for a specific chat.

    Args:
        chat_id (int): The ID of the chat.
        count (int): The new chat count.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    result = await db.inspections.update_one(
        {'chat_id': chat_id},
        {'$set': {'chat_count': count}},
        upsert=True,
    )
    return result.modified_count > 0


async def delete_chat(chat_id: int) -> bool:
    """
    Deletes a chat entry based on the chat_id.

    Args:
        chat_id (int): The ID of the chat to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    result = await db.inspections.delete_one(
        {'chat_id': chat_id},
    )
    return result.deleted_count > 0


async def add_user(
    chat_id: int,
    user_id: int,
    name: Optional[str],
    status: MemberStatus = MemberStatus.Join,
) -> bool:
    """
    Adds a user to a specific chat.

    Args:
        chat_id (int): The ID of the chat.
        user_id (int): The ID of the user to add.
        name (Optional[str]): The name of the user.
        status (Role): The status of the user.

    Returns:
        bool: True if the user was added or updated, False if already exists with the same status.
    """  # noqa: E501
    exist = await get_user(chat_id, user_id)
    if exist and exist.status == status.value:
        return False

    if not name:
        name = 'N/A'
    user = User(
        user_id=user_id,
        name=name,
        status=status.value,
    )
    result = await db.inspections.update_one(
        {'chat_id': chat_id},
        {'$push': {'users': user.dict()}},
        upsert=True,
    )
    return result.modified_count > 0


async def delete_user(chat_id: int, user_id: int) -> bool:
    """
    Deletes a user from a specific chat.

    Args:
        chat_id (int): The ID of the chat.
        user_id (int): The ID of the user to delete.

    Returns:
        bool: True if the user was deleted, False otherwise.
    """
    result = await db.inspections.update_one(
        {'chat_id': chat_id},
        {'$pull': {'users': {'user_id': user_id}}},
    )
    return result.modified_count > 0


async def get_user(chat_id: int, user_id: int) -> Optional[User]:
    """
    Retrieves a user from a specific chat based on user_id.

    Args:
        chat_id (int): The ID of the chat.
        user_id (int): The ID of the user to retrieve.

    Returns:
        Optional[User]: A User object if found, otherwise None.
    """
    document = await db.inspections.find_one(
        {
            'chat_id': chat_id,
            'users.user_id': user_id,
        },
        {'users.$': 1},
    )
    if document and 'users' in document:
        return User(**document['users'][0])

    return None


async def get_all() -> List[Member]:
    """
    Retrieves all chat members.

    Returns:
        List[Member]: A list of Member objects.
    """
    data: List[Member] = []
    async for chat in db.inspections.find():
        data.append(Member(**chat))

    return data
