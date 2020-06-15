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

error_hints = {
    1: '用户名或密码错误。',
    2: '未找到指定的资源。',
    3: '新建卡组时，已有卡组达到99个。',
    4: '编辑随机卡组时，欲添加的卡不在允许范围内',
    5: '编辑随机卡组时，已编辑过2次。',
    6: '非法卡组。',
    7: '已在匹配队列或参与的对局未结束。',
    8: '未处于任何匹配队列或对局。',
}
