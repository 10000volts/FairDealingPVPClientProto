from enum import Enum


class ECardType(Enum):
    LEADER = 1
    EMPLOYEE = 2
    STRATEGY = 3


class ECardRank(Enum):
    COMMON = 0
    GOOD = 1
    TRUMP = 2


card_type = ['', '领袖', '雇员', '策略']
employee_type = {1: '常规', 2: '契约', 4: '继承', 8: '合约', 16: '秘密'}
strategy_type = {1: '常规', 2: '持续', 4: '单人', 8: '反制',
                 16: '契约', 32: '场地'}
