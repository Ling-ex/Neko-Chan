from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from . import data

db = data.afkusers


class AfkUser(BaseModel):
    """Models for away from keyboard"""
    user_id: int
    last_seen: datetime
    reason: Optional[str] = None


async def get(user_id: int) -> Optional[AfkUser]:
    """
    Retrieves the AFK user information based on the provided user_id.

    Args:
        user_id (int): The ID of the user whose AFK information is to be retrieved.

    Returns:
        Optional[AfkUser]: An AfkUser object containing the user's AFK information if found,
        or None if the user is not found in the database.
    """  # noqa: E501
    # Search for user data in the database
    if data := await db.find_one({'user_id': user_id}):
        return AfkUser(**data)

    return None


async def create(
    user_id: int,
    time: datetime,
    reason: Optional[str] = None,
) -> bool:
    """
    Creates or updates the AFK user information in the database.

    Args:
        user_id (int): The ID of the user to be created or updated.
        time (datetime): The last seen time of the user.
        reason (Optional[str]): The reason for the user being AFK (optional).

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    user = AfkUser(
        user_id=user_id,
        last_seen=time,
        reason=reason,
    )
    # Update or insert user data into the database
    return await db.update_one(
        {'user_id': user_id},
        {'$set': user.dict()},
        upsert=True,  # Create if not exists
    )


async def delete(user_id: int) -> bool:
    """
    Deletes the AFK user information from the database based on the provided user_id.

    Args:
        user_id (int): The ID of the user to be deleted.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """  # noqa: E501
    return await db.delete_one({'user_id': user_id})
