import inspect
import io
import os
import sys
import traceback
import uuid
from html import escape
from typing import Any
from typing import List
from typing import Optional

import pyrogram
from meval import meval
from pyrogram import enums
from pyrogram import errors
from pyrogram import filters
from pyrogram import raw
from pyrogram import types

from neko.neko import Client
from neko.utils import time
from neko.utils.filters import owner_only


def format_exception(
    exp: BaseException, tb: Optional[List[traceback.FrameSummary]] = None,
) -> str:
    """
    Formats an exception traceback as a string,
    similar to the Python interpreter.
    """

    if tb is None:
        tb = traceback.extract_tb(exp.__traceback__)

    # Replace absolute paths with relative paths
    cwd = os.getcwd()
    for frame in tb:
        if cwd in frame.filename:
            frame.filename = os.path.relpath(frame.filename)

    stack = ''.join(traceback.format_list(tb))
    msg = str(exp)
    if msg:  # noqa: E501
        msg = f': {msg}'

    return f'Traceback (most recent call last):\n{stack}{type(exp).__name__}{msg}'  # noqa: E501


@Client.on_message(filters.command(['e', 'ev']) & owner_only)
async def eval_handler(c: Client, m: types.Message):
    if len(m.command) == 1:
        return await m.reply_msg("<pre language='python'>None</pre>")

    code = m.text.split(None, 1)[1]
    out_buf = io.StringIO()

    async def _eval() -> tuple[str, Optional[str]]:
        # Message sending helper for convenience
        async def send(*args: Any, **kwargs: Any) -> pyrogram.types.Message:
            return await m.reply_msg(*args, **kwargs)

        def _print(*args: Any, **kwargs: Any) -> None:
            if 'file' not in kwargs:
                kwargs['file'] = out_buf
                return print(*args, **kwargs)

        eval_vars = {
            'c': c,
            'm': m, 'r': m.reply_to_message,
            'u': (m.reply_to_message or m).from_user,
            'raw': raw, 'types': types,
            'stdout': out_buf, 'print': _print,
            'send': send,
            'inspect': inspect, 'os': os, 'sys': sys,
            'traceback': traceback, 'pyro': pyrogram,
        }
        try:
            return '', await meval(code, globals(), **eval_vars)
        except Exception as e:  # skipcq: PYL-W0703
            # Find first traceback frame involving the snippet
            first_snip_idx = -1
            tb = traceback.extract_tb(e.__traceback__)
            for i, frame in enumerate(tb):
                if frame.filename == '<string>' or frame.filename.endswith('ast.py'):  # noqa: E501
                    first_snip_idx = i
                    break
            # Re-raise exception if it wasn't caused by the snippet
            if first_snip_idx == -1:
                raise e
            # Return formatted stripped traceback
            stripped_tb = tb[first_snip_idx:]
            formatted_tb = format_exception(e, tb=stripped_tb)
            return '<b>⚠️ Error executing snippet\n\n', formatted_tb
    before = time.usec()
    prefix, result = await _eval()
    after = time.usec()

    if not out_buf.getvalue() or result is not None:
        print(result, file=out_buf)
    el_us = after - before
    el_str = time.format_duration_us(el_us)
    out = out_buf.getvalue()
    # Strip only ONE final newline to compensate for our message formatting
    if out.endswith('\n'):
        out = out[:-1]
    result = f"""{prefix}<b>In:</b>
<pre language="python">{escape(code)}</pre>
<b>Out:</b>
<pre language="json">{escape(out)}</pre>
Time: {el_str}"""
    if len(result) > 4096:
        with io.BytesIO(str.encode(out)) as out_file:
            out_file.name = str(uuid.uuid4()).split('-')[0].upper() + '.txt'
            caption = f"""{prefix}<b>In:</b>
<pre language="python">{escape(code)}</pre>

Time: {el_str}"""
            if len(caption) > 4096:
                caption = 'Input is to long'
            try:
                await m.reply_document(
                    document=out_file,
                    caption=caption,
                    disable_notification=True,
                    parse_mode=enums.parse_mode.ParseMode.HTML,
                )
            except errors.MediaCaptionTooLong:
                await m.reply_document(
                    document=out_file,
                    caption='input is to long',
                    disable_notification=True,
                    parse_mode=enums.parse_mode.ParseMode.HTML,
                )
        return None
    return await m.reply_msg(
        result,
        parse_mode=enums.parse_mode.ParseMode.HTML,
    )
