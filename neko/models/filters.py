from typing import List, Optional
from pydantic import BaseModel
from . import data

db = data.filters

class Filter(BaseModel):
    chat_id: int
    keyword: str
    reply_text: str

async def add_filter(chat_id: int, keyword: str, reply_text: str) -> None:
    """Tambah atau perbarui filter."""
    await db.update_one(
        {'chat_id': chat_id, 'keyword': keyword},
        {'$set': {'reply_text': reply_text}},
        upsert=True
    )

async def get_filter(chat_id: int, keyword: str) -> Optional[Filter]:
    """Ambil filter tertentu berdasarkan chat_id dan keyword."""
    data = await db.find_one({'chat_id': chat_id, 'keyword': keyword})
    return Filter(**data) if data else None

async def get_all_filters(chat_id: int) -> List[Filter]:
    """Ambil semua filter untuk chat tertentu."""
    filters = await db.find({'chat_id': chat_id}).to_list(None)
    return [Filter(**f) for f in filters]

async def delete_filter(chat_id: int, keyword: str) -> bool:
    """Hapus filter tertentu."""
    result = await db.delete_one({'chat_id': chat_id, 'keyword': keyword})
    return result.deleted_count > 0

async def delete_all_filters(chat_id: int) -> None:
    """Hapus semua filter untuk chat tertentu."""
    await db.delete_many({'chat_id': chat_id})