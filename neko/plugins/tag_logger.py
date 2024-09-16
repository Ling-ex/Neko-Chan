import re

from pyrogram import enums
from pyrogram import types
from pyrogram import filters
from pyrogram.helpers import ikb

from neko.neko import Client


# Handler tag user logger
@Client.on_message(
    filters.group
    & ~filters.bot & ~filters.via_bot
    & filters.text
    & filters.incoming
    group=99,
)
async def tag_logger_handler(c: Client, m: types.Message):
    user: types.User = None
    if entity := m.entities:
        num = 0
        for _ in range(len(entity)):
            if (entity[num].type) == enums.MessageEntityType.MENTION:
                found = re.findall('@([_0-9a-zA-Z]+)', m.text)
                try:
                    user = await c.get_users(found[num])
                    if user == m.from_user.id:
                        user = None
                except:
                    num += 1
                    continue
            elif (entity[num].type) == enums.MessageEntityType.TEXT_MENTION:
                user = entity[num].user
                if user.id == m.from_user.id:
                    user = None

    if user is None:
        return m.stop_propagation()
    if m.from_user and user.id == m.from_user.id:
        return m.stop_propagation()
    if m.from_user:
        tag_by = "@" + m.from_user.username if m.from_user.username else m.from_user.mention
    else:
        tag_by = "Anon"
    text = f"""
<b><u>You have been tagged</u></b>
• <b>From:</b> {tag_by}
• <b>Group:</b> {m.chat.title}"""
    try:
        msg = await c.send_message(
            user.id,
            text,
            reply_markup=ikb([[('👉🏻 Go to messages', m.link, 'url')]]),
        )
        return msg
    except (
        errors.PeerIdInvalid,
        errors.UserIsBlocked,
        errors.InputUserDeactivated,
    ):
        pass
    except Exception as e:
        c.log.info(f"admin (report): {str(e)}")
