from importlib import import_module

from .plugins import load_plugins


CMD_HELP = {}

async def init_plugins():
    for plugin in load_plugins():
        imported_module = import_module(f'neko.plugins.' + plugin)
        if hasattr(imported_module, '__PLUGINS__') and imported_module.__MODULE__:
            imported_module.__MODULE__ = imported_module.__MODULE__
            if hasattr(imported_module, '__HELP__') and imported_module.__HELP__:
                CMD_HELP[
                    imported_module.__MODULE__.replace(' ', '_').lower()
                ] = imported_module