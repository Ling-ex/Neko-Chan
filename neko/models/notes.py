from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from . import data


db = data.notes


class Notes(BaseModel):
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
    type: Optional[str] = None,
) -> bool:
    note = Notes(
        chat_id=chat_id,
        name=name,
        value=value,
        media=media,
        type=type,
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
    if data := await db.find_one({'chat_id': chat_id, 'name': name}):
        return Notes(**data)

    return None


async def delete_by_name(
    chat_id: int,
    name: str,
) -> bool:
    return await db.delete_one({'chat_id': chat_id, 'name': name})


async def get_all_by_chat(chat_id: int) -> List[Notes]:
    data = await db.find({'chat_id': chat_id}).to_list(None)

    return [Notes(**doc) for doc in data]
