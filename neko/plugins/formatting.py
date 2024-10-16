from pyrogram import filters, enums
from pyrogram.types import Message

from neko.neko import Client

@Client.on_message(filters.command("formatting") & filters.private)
async def formatting_help(_, m: Message):
    text = """
<b>HTML and Placeholder Formatting Guide</b>

You can use the following formats in your messages:

<b>Bold:</b>
<code>&lt;b&gt;text&lt;/b&gt;</code> → <b>text</b>

<i>Italic:</i>
<code>&lt;i&gt;text&lt;/i&gt;</code> → <i>text</i>

<u>Underline:</u>
<code>&lt;u&gt;text&lt;/u&gt;</code> → <u>text</u>

<s>Strikethrough:</s>
<code>&lt;s&gt;text&lt;/s&gt;</code> → <s>text</s>

<b>Code Block:</b>
<code>&lt;code&gt;inline code&lt;/code&gt;</code> → <code>inline code</code>

<pre>&lt;pre&gt;multi-line code&lt;/pre&gt;</pre> → 
<pre>
multi-line code
</pre>

<b>Links:</b>
<code>&lt;a href="https://google.com"&gt;Google&lt;/a&gt;</code> → <a href="https://google.com">Google</a>

<b>Placeholders:</b>
- <code>{first}</code>: User's first name → {first}
- <code>{username}</code>: User's username or mention → {username}
- <code>{id}</code>: User ID → {id}
- <code>{chatname}</code>: Chat's name → {chatname}

<b>Adding Inline Buttons in Filters:</b>
To add buttons, use the following format:
<code>[button:Text,URL]</code>

<b>Examples:</b>
<code>/filter example This is a message [button:Google,https://google.com]</code> 
→ Adds a filter with a button linking to Google.

<code>/filter example Multi-button [button:Google,https://google.com|Bing,https://bing.com]</code> 
→ Adds multiple buttons in a single row.

<code>/filter example Multiple rows [button:Google,https://google.com;YouTube,https://youtube.com]</code> 
→ Adds buttons in multiple rows.

<b>Note:</b> 
- HTML parsing is supported.
- Placeholders will be replaced dynamically when the message is sent.
"""

    await m.reply(text, parse_mode=enums.ParseMode.HTML)