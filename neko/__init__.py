
from importlib import import_module

from .plugins import load_plugins

CMD_HELP = {}

def get_client():
    """
    Fungsi untuk impor dan mengembalikan kelas Client.
    """
    from .neko import Client
    return Client

async def init_plugins():
    """
    Loads the list of available plugins from the current directory.
    """

    for plugin in load_plugins():
        imported_module = import_module('neko.plugins.' + plugin)
        if (
            hasattr(imported_module, '__MODULE__') and
            imported_module.__MODULE__
        ):
            imported_module.__MODULE__ = imported_module.__MODULE__
            if (
                hasattr(imported_module, '__HELP__') and
                imported_module.__HELP__
            ):
                CMD_HELP[
                    imported_module.__MODULE__.replace(' ', '_').lower()
                ] = imported_module