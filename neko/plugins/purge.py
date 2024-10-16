from asyncio import sleep
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError

from neko.utils.filters import admins_only
from neko.utils import func
from neko.neko import Client

@Client.on_message(filters.command("purge") & filters.group & admins_only)
async def purge(client: Client, message: Message):
    await func.require_admin('can_delete_messages')(client, message)

    if not message.reply_to_message:
        await message.reply_text("Reply to a message to delete all following messages.")
        return

    await message.delete()

    purge_count = 0
    for msg_id in range(message.reply_to_message.id, message.id):
        try:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=msg_id,
                revoke=True
            )
            purge_count += 1
            await sleep(0.1)
        except MessageDeleteForbidden:
            await message.reply_text("I don't have permission to delete some messages.")
        except RPCError as e:
            print(f"Failed to delete message {msg_id}: {e}")

    confirmation = await client.send_message(
        chat_id=message.chat.id,
        text=f"Purged <b>{purge_count}</b> messages.",
        parse_mode="html"
    )
    await sleep(3)
    await confirmation.delete()

@Client.on_message(filters.command("del") & filters.group & admins_only)
async def delete_message(client: Client, message: Message):
    await func.require_admin('can_delete_messages')(client, message)

    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except MessageDeleteForbidden:
            await message.reply_text("I don't have permission to delete that message.")
        except RPCError as e:
            print(f"Failed to delete message: {e}")
    else:
        await message.reply_text("Reply to a message to delete it.")