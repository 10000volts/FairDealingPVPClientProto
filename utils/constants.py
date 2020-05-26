from enum import Enum


class ECardType(Enum):
    LEADER = 1
    EMPLOYEE = 2
    STRATEGY = 3


card_type = ['', '领袖', '雇员', '策略']
employee_type = ['', '常规', '契约', '继承', '合约']
strategy_type = ['', '常规', '持续', '单人', '反制', '反制|持续', '立即',
                 '立即|持续', '契约', '场地']
