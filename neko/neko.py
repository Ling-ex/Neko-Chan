import logging
import os

import aiofiles  # type: ignore
import colorlog
from pyrogram import Client as RawClient
from pyrogram import errors
from pyrogram import raw

from .core.schedule import Scheduler
from .models import connection
from config import Config


log = logging.getLogger('Neko')


class Client(RawClient, Scheduler):
    def __init__(self) -> None:
        super().__init__(  # type: ignore
            'Neko_Session',
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(
                root='neko.plugins',
            ),
            mongodb=dict(
                connection=connection,
                remove_peers=False,
            ),
            in_memory=False,
            sleep_threshold=180,
        )
        self.config = Config
        self.db = connection.neko
        self.log = log

    async def start(self) -> None:
        self._setup_log()
        self.log.info('Starting bot...')
        await super().start()
        self.log.info('---[Bot Started]---')
        await self.catch_up()
        self.log.info('---[Gaps Restored]---')
        await self.read_pickup()
        await self.start_sch()

    async def stop(self, block: bool = False) -> None:
        self.log.info('---[Saving state...]---')
        db = self.db.bot_settings
        state = await self.invoke(raw.functions.updates.GetState())
        value = {
            'pts': state.pts,
            'qts': state.qts,
            'date': state.date,
        }
        await db.update_one(
            {'name': 'state'},
            {
                '$set': {'value': value},
            },
            upsert=True,
        )
        await super().stop(block=block)
        self.log.info('---[Bot Stopped]---')

    def _setup_log(self):
        """Configures logging"""
        level = logging.WARNING
        logging.root.setLevel(level)

        # Color log config
        log_color: bool = True

        file_format = '[ %(asctime)s: %(levelname)-8s ] %(name)-15s - %(message)s'  # noqa: E501
        logfile = logging.FileHandler('neko.txt')
        formatter = logging.Formatter(file_format, datefmt='%H:%M:%S')
        logfile.setFormatter(formatter)
        logfile.setLevel(level)

        if log_color:
            formatter = colorlog.ColoredFormatter(
                '  %(log_color)s%(levelname)-8s%(reset)s  |  '
                '%(name)-15s  |  %(log_color)s%(message)s%(reset)s',
            )
        else:
            formatter = logging.Formatter(
                '  %(levelname)-8s  |  %(name)-15s  |  %(message)s',
            )
        stream = logging.StreamHandler()
        level = logging.INFO
        stream.setLevel(level)
        stream.setFormatter(formatter)

        root = logging.getLogger()
        root.setLevel(level)
        root.addHandler(stream)
        root.addHandler(logfile)

        # Logging necessary for selected libs
        logging.getLogger('pyrogram').setLevel(logging.ERROR)
        logging.getLogger('apscheduler').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.ERROR)

    async def catch_up(self):
        self.log.info('---[Recovering gaps...]---')
        db = self.db.bot_settings
        state = await db.find_one({'name': 'state'})
        if not state:
            return
        value = state['value']
        pts = value['pts']
        date = value['date']
        prev_pts = 0
        diff = None
        while True:
            try:
                diff = await self.invoke(
                    raw.functions.updates.GetDifference(
                        pts=pts,
                        date=date,
                        qts=0,
                    ),
                )
            except errors.PersistentTimestampInvalid:
                continue
            if isinstance(diff, raw.types.updates.DifferenceEmpty):
                await db.delete_one({'name': 'state'})
                break
            elif isinstance(diff, raw.types.updates.DifferenceTooLong):
                pts = diff.pts
                continue
            users = {u.id: u for u in diff.users}
            chats = {c.id: c for c in diff.chats}
            if isinstance(diff, raw.types.updates.DifferenceSlice):
                new_state = diff.intermediate_state
                pts = new_state.pts
                date = new_state.date
                # Stop if current pts is same with previous loop
                if prev_pts == pts:
                    await db.delete_one({'name': 'state'})
                    break
                prev_pts = pts
            else:
                new_state = diff.state
            for msg in diff.new_messages:
                self.dispatcher.updates_queue.put_nowait((
                    raw.types.UpdateNewMessage(
                        message=msg,
                        pts=new_state.pts,
                        pts_count=-1,
                    ),
                    users,
                    chats,
                ))

            for update in diff.other_updates:
                self.dispatcher.updates_queue.put_nowait(
                    (update, users, chats),
                )
            if isinstance(diff, raw.types.updates.Difference):
                await db.delete_one({'name': 'state'})
                break

    async def read_pickup(self) -> None:
        """
        Reads the chat ID and message ID from 'pickup.txt'
        and edits the message
        to indicate that the server has restarted successfully.
        If the file does not exist, it exits without doing anything.
        After processing, the file is deleted.
        """
        file = 'pickup.txt'
        if not os.path.exists(file):
            return
        self.log.info('Reading from pickup.txt ....')
        try:
            async with aiofiles.open(file, 'r') as rd:
                content = await rd.read()
                chat_id, msg_id = map(int, content.strip().split('\n'))
                await self.edit_message_text(
                    chat_id,
                    msg_id,
                    'Server restarted successfully!',
                )
        except Exception as e:
            self.log.info(f'Error reading from pickup.txt: {e}')
        os.remove(file)
