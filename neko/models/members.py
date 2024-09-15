from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from . import data as db


# Enum for Role Updates
class Role(str, Enum):
    JOIN = 'JOIN'
    LEAVE = 'LEAVE'
    RESTRICTED = 'RESTRICTED'

# Model for User


class User(BaseModel):
    user_id: int
    name: str
    status: Role = Role.JOIN

# Model for Member


class Member(BaseModel):
    chat_id: int
    chat_count: int = Field(default=0)
    users: List[User] = Field(default_factory=list)


async def get_chat(chat_id: int) -> Optional[Member]:
    document = await db.inspections.find_one(
        {'chat_id': chat_id},
    )
    if document:
        return Member(**document)

    return None


async def add_chat(chat_id: int, count: int) -> bool:
    result = await db.inspections.update_one(
        {'chat_id': chat_id},
        {'$set': {'chat_count': count}},
        upsert=True,
    )
    return result.modified_count > 0


async def delete_chat(chat_id: int) -> bool:
    result = await db.inspections.delete_one(
        {'chat_id': chat_id},
    )
    return result.deleted_count > 0


async def add_user(
    chat_id: int,
    user_id: int,
    name: str,
    status: Role = Role.JOIN,
) -> bool:
    exist = await get_user(chat_id, user_id)
    if exist and exist.status == status:
        return False
    user = User(
        user_id=user_id,
        name=name,
        status=status,
    )
    result = await db.inspections.update_one(
        {'chat_id': chat_id},
        {'$push': {'users': user.dict()}},
        upsert=True,
    )
    return result.modified_count > 0


async def delete_user(chat_id: int, user_id: int) -> bool:
    result = await db.inspections.update_one(
        {'chat_id': chat_id},
        {'$pull': {'users': {'user_id': user_id}}},
    )
    return result.modified_count > 0


async def get_user(chat_id: int, user_id: int) -> Optional[User]:
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
    data: List[Member] = []
    async for chat in db.inspections.find():
        data.append(Member(**chat))

    return data
