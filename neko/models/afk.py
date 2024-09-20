from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from . import data

db = data.afkusers


class AfkUser(BaseModel):
    user_id: int
    last_seen: datetime
    reason: Optional[str] = None


async def get(user_id: int) -> Optional[AfkUser]:
    if data := await db.find_one({'user_id': user_id}):
        return AfkUser(**data)

    return None


async def create(
    user_id: int,
    time: datetime,
    reason: Optional[str] = None,
) -> bool:
    user = AfkUser(
        user_id=user_id,
        last_seen=time,
        reason=reason,
    )
    return await db.update_one(
        {'user_id': user_id},
        {'$set': user.dict()},
        upsert=True,
    )


async def delete(user_id: int) -> bool:
    return await db.delete_one({'user_id': user_id})
