from pyrogram import filters, enums
from pyrogram.types import Message

from neko.neko import Client
from neko.utils import func

@Client.on_message(filters.command("formatting") & filters.private)
async def formatting_help(_, m: Message):
    text = """
<b>Markdown and Placeholder Formatting Guide</b>

You can use the following formats in your messages:

<b>Bold:</b>
<code>**text**</code> → <b>text</b>

<i>Italic:</i>
<code>*text*</code> → <i>text</i>

<u>Underline:</u>
<code>__text__</code> → <u>text</u>

<s>Strikethrough:</s>
<code>~~text~~</code> → <s>text</s>

<b>Code Block:</b>
<code>`inline code`</code> → <code>inline code</code>

<pre>```multi-line code```</pre> → 
<pre>
multi-line code
</pre>

<b>Links:</b>
<code>[Google](https://google.com)</code> → <a href="https://google.com">Google</a>

<b>Placeholders:</b>
- <code>{first}</code>: User's first name → {first}
- <code>{username}</code>: User's username or mention → {username}
- <code>{id}</code>: User ID → {id}
- <code>{chatname}</code>: Chat's name → {chatname}

<b>Note:</b> 
- HTML and Markdown parsing are supported.
- Placeholders will be replaced dynamically when the message is sent.
"""

    await m.reply(text, parse_mode=enums.ParseMode.HTML)