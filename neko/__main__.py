from .neko import Client


try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()

if __name__ == '__main__':
    bot = Client()
    try:
        bot.run()
    except KeyboardInterrupt:
        pass
    finally:
        bot.loop.stop()
