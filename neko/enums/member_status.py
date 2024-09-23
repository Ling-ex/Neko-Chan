from enum import auto

from .auto_name import AutoName


class MemberStatus(AutoName):
    Join = auto()
    'The member has joined'

    Left = auto()
    'The member has left'

    Restricted = auto()
    'The member is restricted'
