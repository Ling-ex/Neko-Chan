from asyncio import sleep
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message
from neko.utils import func

@Client.on_message(filters.command("purge") & ~filters.private)
@func.require_admin('can_delete_messages')
async def purge_handler(c: Client, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        await m.reply_text("Cannot purge messages in a basic group.")
        return

    if not m.reply_to_message:
        await m.reply_text("Reply to a message to start purging!")
        return

    message_ids = list(range(m.reply_to_message.id, m.id))

    def divide_chunks(lst, n=100):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    message_chunks = list(divide_chunks(message_ids))

    try:
        for chunk in message_chunks:
            await c.delete_messages(
                chat_id=m.chat.id,
                message_ids=chunk,
                revoke=True,
            )
        await m.delete()
    except MessageDeleteForbidden:
        await m.reply_text(
            "Cannot delete all messages. Messages may be too old, or I might not have the right permissions."
        )
    except RPCError as e:
        await m.reply_text(
            f"An error occurred:\n\n<b>Error:</b> <code>{e}</code>"
        )

    count_del_msg = len(message_ids)
    confirmation = await m.reply_text(f"Deleted <i>{count_del_msg}</i> messages.")
    await sleep(3)
    await confirmation.delete()

@Client.on_message(filters.command("del") & ~filters.private)
@func.require_admin('can_delete_messages')
async def delete_message_handler(c: Client, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        return

    if m.reply_to_message:
        await c.delete_messages(m.chat.id, [m.reply_to_message.id, m.id])
    else:
        await m.reply_text("Reply to a message to delete it!")