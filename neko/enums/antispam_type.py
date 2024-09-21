from enum import auto

from .auto_name import AutoName


class AntiSpamType(AutoName):
    AntiChannel = auto()
    'For anti-channel'

    AntiForward = auto()
    'For anti-forward'
