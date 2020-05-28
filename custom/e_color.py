from enum import Enum


class EColor(Enum):
    """
    0(默认)、30(黑)、31(红)、32(绿)、33(黄)、
    34(蓝)、35(洋红)、36(青)、37(白)、38(黑)
    """

    # dc
    DEFAULT_COLOR = 34
    # em
    PLAYER_NAME = 33
    # emn
    EMPHASIS = 33
    # err
    ERROR = 31

    # ct
    TRUMP_CARD = 35
    # cg
    GOOD_CARD = 36
    # cc
    COMMON_CARD = 37

    # atk
    ATK = 31
    # def
    DEF = 36