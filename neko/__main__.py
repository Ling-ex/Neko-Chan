
import asyncio
from neko import get_client

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

async def main():
    Client = get_client()
    bot = Client()
    try:
        await bot.start()
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        if bot.is_connected:
            await bot.stop()

if __name__ == '__main__':
    asyncio.run(main())