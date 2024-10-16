from pydantic import BaseModel
from typing import Optional
from . import data

db = data.greetings_settings

class GreetingSettings(BaseModel):
    chat_id: int
    welcome_message: Optional[str] = None
    goodbye_message: Optional[str] = None
    cleanwelcome_on: bool = False
    cleangoodbye_on: bool = False
    welcome_off: bool = False
    goodbye_off: bool = False
    cleanservice_on: bool = False
    last_welcome: Optional[int] = None
    last_goodbye: Optional[int] = None

async def get_greeting_settings(chat_id: int):
    data = await db.find_one({"chat_id": chat_id})
    if data:
        return GreetingSettings(**data)
    default_settings = GreetingSettings(chat_id=chat_id)
    await update_greeting_settings(chat_id, default_settings.dict())
    return default_settings

async def update_greeting_settings(chat_id: int, settings: dict):
    await db.update_one(
        {"chat_id": chat_id},
        {"$set": settings},
        upsert=True
    )
