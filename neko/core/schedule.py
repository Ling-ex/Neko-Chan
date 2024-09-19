import asyncio
from datetime import datetime
from datetime import timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import errors

from config import Config
from neko.models import members


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
        # only run at 00:15
        self.scheduler.add_job(
            self.update_members,
            'cron', hour=0, minute=15,
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

    async def update_members(self) -> None:
        now = datetime.utcnow() + timedelta(hours=7)
        time = now.strftime('📆 %Y-%m-%d | ⏱ %H:%M:%S')
        for chat in await members.get_all():
            try:
                count = await self.get_chat_members_count(  # type: ignore
                    chat.chat_id,
                )
            except Exception:
                continue

            count_db = chat.chat_count
            amount = count - count_db
            if count_db < count:
                react = '<b><i>🙂 Congratulations 🎉</i></b>'
                mark = (
                    'experienced <u><b>increase</b></u> by as much: '
                    f'<code>{amount} members</code> when compared'
                )
            elif count_db > count:
                react = '<b><i>🙁 Yaahhh!</i></b>'
                mark = (
                    'experienced <u><b>decrease</b></u> by as much: '
                    f'<code>{amount} members</code> when compared'
                )
            else:
                react = '<b><i>😐 Hmmm!</i></b>'
                mark = '<u><b>still the same</b></u>'

            text = (
                '<i>✅ Group check <b>is complete!</b></i>\n\n'
                f'<code>{time}</code>\n\n'
                f'<i>{react}\n'
                f'The current number of members {mark} compared'
                f' to yesterday is: <code>{count_db}</code> members</i>\n\n'
            )
            joined_members = []
            leaving_members = []
            banned_members = []
            for user in chat.users:
                if user.status == members.Role.LEAVE:
                    leaving_members.append(user)
                elif user.status == members.Role.RESTRICTED:
                    banned_members.append(user)
                elif user.status == members.Role.JOIN:
                    joined_members.append(user)
                await members.delete_user(chat.chat_id, user.user_id)

            if joined_members:
                new_members_list = '\n'.join(
                    [
                        f'{i}. <b>{user.name}</b> | <code>{user.user_id}</code>'  # noqa: E501
                        for i, user in enumerate(joined_members, 1)
                    ],
                )
                text += (
                    '<b><u>✳️ New Members:</u></b>\n'
                    f'{new_members_list}\n\n'
                )

            if banned_members:
                banned_members_list = '\n'.join(
                    [
                        f'{i}.  <b>{user.name}</b> | <code>{user.user_id}</code>'  # noqa: E501
                        for i, user in enumerate(banned_members, 1)
                    ],
                )
                text += (
                    '<b><u>🚫 Banned Members:</u></b>\n'
                    f'{banned_members_list}\n\n'
                )

            if leaving_members:
                leaving_members_list = '\n'.join(
                    [
                        f'{i}. <b>{user.name}</b> | <code>{user.user_id}</code>'  # noqa: E501
                        for i, user in enumerate(leaving_members, 1)
                    ],
                )
                text += (
                    '<b><u>⚠️ Members Left:</u></b>\n'
                    f'{leaving_members_list}\n\n'
                )
            await members.add_chat(chat.chat_id, count)
            await self.send_animation(  # type: ignore
                chat.chat_id,
                animation='https://telegra.ph/file/8bf32e00ad2ca725046d3.mp4',
                caption=text,
            )
