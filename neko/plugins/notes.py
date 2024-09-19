import re
from typing import Optional
from typing import Tuple

from pyrogram import enums
from pyrogram import errors
from pyrogram import filters
from pyrogram import types
from pyrogram.helpers import ikb

from neko.models import notes
from neko.neko import Client
from neko.utils.filters import owner_chats
from neko.utils.filters import admins_only
from neko.utils.misc_bttn import dynamic_buttons


__MODULE__ = "Notes"
__HELP__ = """
▎<b>Notes</b>
- <b>Add a note:</b>
   /save {key} {text/reply/caption

- <b>Get a note:</b>
   /get {key} or #key

- <b>Delete a note:</b>
  /delnote {key}

- <b>Get all notes by chat:</b>
   /notes

- <b>Delete all notes by chat:</b>
   /clearall ; only owner
"""


def get_media_info(
    msg: types.Message,
) -> Optional[Tuple[str, str]]:
    if reply := msg.reply_to_message:
        event = reply
    else:
        event = msg

    if not (args := event.media):
        return None

    info = getattr(event, event.media.value, None)
    if info is None:
        return None

    media_types = {
        enums.MessageMediaType.PHOTO: 'photo',
        enums.MessageMediaType.VIDEO: 'video',
        enums.MessageMediaType.STICKER: 'sticker',
        enums.MessageMediaType.ANIMATION: 'animation',
        enums.MessageMediaType.DOCUMENT: 'document',
        enums.MessageMediaType.AUDIO: 'audio',
        enums.MessageMediaType.VOICE: 'voice',
        enums.MessageMediaType.VIDEO_NOTE: 'video note',
        enums.MessageMediaType.WEB_PAGE_PREVIEW: 'text',
    }

    media_type = media_types.get(args)
    if media_type is None:
        return None

    return info.file_id, media_type


def get_message_text(msg: types.Message) -> Optional[str]:
    if rep := msg.reply_to_message:
        if rep.text:
            return rep.text.html
        elif rep.caption:
            return rep.caption.html
    else:
        if len(msg.command) > 2:
            if msg.text:
                return msg.text.html.split(None, 2)[2]
            elif msg.caption:
                return msg.caption.html.split(None, 2)[2]
            else:
                return None

    return None


@Client.on_message(filters.command('save') & admins_only)
async def save_notes_handler(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_msg(
            'Please provide a name for the note to save!',
        )

    name = m.command[1]
    value = get_message_text(m)
    media_info = get_media_info(m)

    if media_info is not None:
        file_id, type = media_info
    else:
        file_id, type = None, 'text'

    await notes.create(
        m.chat.id,
        name,
        value,
        file_id,
        type,
    )
    return await m.reply_msg(
        f'Note {name} saved.',
    )


@Client.on_message(
    filters.regex(r'^(/get\s.+|#.+)')
    & filters.text & ~filters.private,
)
async def get_note_handler(_, m: types.Message):
    if m.text.startswith('/get '):
        name = m.text.replace('/get ', '', 1)
    elif m.text.startswith('#'):
        name = m.text.replace('#', '', 1)
    else:
        return

    if not (data := await notes.get_by_name(m.chat.id, name)):
        return
    value = data.value
    media = data.media
    type = data.type
    if value and re.findall(r'\[(.*?)\]\(buttonurl:(.*?)\)', value.lower()):
        text, button = await dynamic_buttons(value)
    else:
        text, button = value, None

    user = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    username = '@' + user.username if user.username else 'N/A'
    _format = {
        'id': user.id,
        'first': user.first_name,
        'last': user.last_name,
        'fullname': user.full_name,
        'username': username,
        'mention': user.mention,
        'chatname': m.chat.title,
    }
    if text:
        try:
            text = text.format(**_format)
        except KeyError:
            text = text
    if type == 'text':
        try:
            await m.reply_msg(
                text,
                reply_markup=button,
                disable_web_page_preview=True,
            )
        except errors.ButtonUrlInvalid:
            return await m.reply_msg(
                value,
                disable_web_page_preview=True,
            )
    elif type == 'photo':
        try:
            await m.reply_photo(
                media,
                caption=text,
                reply_markup=button,
            )
        except errors.ButtonUrlInvalid:
            return await m.reply_photo(
                media,
                caption=value,
            )
    elif type == 'video':
        try:
            await m.reply_video(
                media,
                caption=text,
                reply_markup=button,
            )
        except errors.ButtonUrlInvalid:
            return await m.reply_video(
                media,
                caption=value,
            )
    elif type == 'sticker':
        return await m.reply_sticker(
            media,
        )
    elif type == 'animation':
        try:
            await m.reply_animation(
                media,
                caption=text,
                reply_markup=button,
            )
        except errors.ButtonUrlInvalid:
            return await m.reply_animation(
                media,
                caption=value,
            )
    elif type == 'document':
        try:
            await m.reply_document(
                media,
                caption=text,
                reply_markup=button,
            )
        except errors.ButtonUrlInvalid:
            return await m.reply_document(
                media,
                caption=value,
            )
    elif type == 'voice':
        try:
            await m.reply_voice(
                media,
                caption=text,
                reply_markup=button,
            )
        except errors.ButtonUrlInvalid:
            return await m.reply_voice(
                media,
                caption=value,
            )
    elif type == 'video note':
        return await m.reply_video_note(
            media,
        )
    elif type == 'audio':
        try:
            return await m.reply_audio(
                media,
                caption=text,
                reply_markup=button,
            )
        except errors.ButtonUrlInvalid:
            return await m.reply_audio(
                media,
                caption=value,
            )


@Client.on_message(filters.command('delnote') & admins_only)
async def delete_note_handler(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_msg(
            'Please provide the name of the note you want to delete.',
        )
    name = m.command[1]
    done = await notes.delete_by_name(m.chat.id, name)
    if not done:
        return await m.reply_msg(
            f'Note with name {name} not found',
        )
    return await m.reply_msg(
        f'The note with the name {name} was successfully deleted.',
    )


@Client.on_message(filters.command('notes'))
async def get_all_noted(_, m: types.Message):
    chat = m.chat
    all_notes: list = await notes.get_all_by_chat(chat.id)
    if not all_notes:
        return await m.reply_msg(
            f'Notes in empty {chat.title}',
        )
    text = f'<b>List of notes {chat.title}:</b>\n\n'
    for note in all_notes:
        text += f'• <code>{note.name}<code> | ({note.type})\n'
    return await m.reply_msg(text)


@Client.on_message(filters.command('clearall') & owner_chats)
async def delete_all_notes(_, m: types.Message):
    if not await notes.get_all_by_chat(m.chat.id):
        return await m.reply_msg(
            f'Noted in empty {m.chat.title}',
        )

    return await m.reply_msg(
        'Are you sure you would like to clear ALL notes in {}? This action cannot be undone.'.format(  # noqa: E501
            m.chat.title,
        ),
        reply_markup=ikb(
            [
                [('Delete all notes', 'ClearAll yes')],
                [('Cancel', 'ClearAll cancel')],
            ],
        ),
    )


@Client.on_callback_query(filters.regex(r'^ClearAll') & owner_chats)
async def cb_delete_all_notes(_, cb: types.CallbackQuery):
    action = cb.data.strip().split()[1]
    chat = cb.message.chat
    if action == 'yes':
        await notes.db.delete_many({'chat_id': chat.id})
        return await cb.message.edit_msg(
            f'Deleted all chat notes in {chat.title}',
        )
    else:
        return await cb.message.edit_msg(
            'Clearing of all notes has been cancelled.',
        )
