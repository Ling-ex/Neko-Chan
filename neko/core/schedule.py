import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import errors

from config import Config


class Manager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone='Asia/Jakarta')


class Scheduler(Manager):

    async def start_sch(self) -> None:
        # only run at 00:00
        self.scheduler.add_job(
            self.deleted_account,
            'cron', hour=0, minute=0,
        )
        # run the schedule im asyncIO
        self.scheduler.start()

    async def deleted_account(self) -> None:
        CHAT_ID = Config.CHAT_ID
        get_members = None
        try:
            mem = await self.get_chat_members_count(CHAT_ID)  # type: ignore
            # Only cleans groups with less than 4000 members
            # Because Telegram's limit is only ~4000 members
            if mem <= 4000:
                get_members = self.get_chat_members(CHAT_ID)  # type: ignore
        except errors.FloodWait as f:
            await asyncio.sleep(f.value)
            mem = await self.get_chat_members_count(CHAT_ID)  # type: ignore
            # Only cleans groups with less than 4000 members
            # Because Telegram's limit is only ~4000 members
            if mem <= 4000:
                get_members = self.get_chat_members(CHAT_ID)  # type: ignore
        except Exception as er:
            self.log.error(str(er))  # type: ignore

        count = 0
        if not get_members:
            return
        async for member in get_members:
            try:
                if member.user.is_deleted:
                    await self.ban_chat_member(  # type: ignore
                        CHAT_ID,
                        member.user.id,
                    )
                    count += 1
            except errors.FloodWait as f:
                await asyncio.sleep(f.value)
                if member.user.is_deleted:
                    await self.ban_chat_member(  # type: ignore
                        CHAT_ID,
                        member.user.id,
                    )
                    count += 1
            except (
                errors.UserAdminInvalid,
                errors.ChatAdminRequired,
            ):
                continue
            except Exception as e:
                self.log.error(str(e))  # type: ignore
        if count < 1:
            text = 'This group is clean of murdered members.'
        else:
            text = 'Find {} Member killed and get rid of him/her.'.format(
                count,
            )

        await self.send_message(  # type: ignore
            CHAT_ID,
            text,
        )
