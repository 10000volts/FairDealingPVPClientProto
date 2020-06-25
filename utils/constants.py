from enum import Enum


class ECardType(Enum):
    LEADER = 1
    EMPLOYEE = 2
    STRATEGY = 3


class ECardRank(Enum):
    COMMON = 0
    GOOD = 1
    TRUMP = 2


card_rank = ['普通', '优质', '王牌']
card_type = ['', '领袖', '雇员', '策略']
employee_type = {1: '常规', 2: '契约', 4: '继承', 8: '合约', 16: '秘密'}
strategy_type = {1: '常规', 2: '持续', 4: '单人', 8: '反制',
                 16: '契约', 32: '场地'}
location = {5: '场上', 9: '手牌', 17: '场下', 33: '移除', 65: '卡组',
            129: '备选卡组', 257: '未知', 6: '场上', 10: '手牌', 18: '场下', 34: '移除', 66: '卡组',
            130: '备选卡组', 258: '未知'}
effect_desc = {1: '调查筹码'}

error_hints = {
    1: '用户名或密码错误。',
    2: '未找到指定的资源。',
    3: '新建卡组时，已有卡组达到99个。',
    4: '编辑随机卡组时，欲添加的卡不在允许范围内',
    5: '编辑随机卡组时，已编辑过2次。',
    6: '非法卡组。',
    7: '已在匹配队列或参与的对局未结束。',
    8: '未处于任何匹配队列或对局。',
    9: '错误输入',
}

game_phase = {
    0: '先后手决定阶段',
    1: '初始化阶段',
    2: '公示阶段',
    3: '额外生成阶段',
    4: '放置筹码阶段',
    5: '取走筹码阶段',
    6: '调整阶段',
    7: '使用筹码阶段'
}

time_point = {
    0: '起始阶段时',
    5: '先后手决定阶段开始时',
    10: '先后手决定阶段结束时',
    15: '公示阶段开始时',
    20: '公示阶段结束时',
    25: '额外生成阶段开始时',
    27: '附加值生成时',
    30: '附加值生成后',
    40: '调查筹码生成后',
    43: '额外生成阶段结束时',
    46: '放置筹码阶段开始时',
    50: '单个筹码被放置后',
    60: '所有筹码被放下后，附加值结算时',
    70: '附加值阶段后，放置筹码阶段末尾',
    75: '取走筹码阶段开始时',
    80: '对筹码的一次取走操作完成后',
    90: '取走筹码阶段结束时',
    100: '调整阶段开始时',
    110: '调整阶段结束时',
    115: '使用筹码阶段开始时',
    120: '尝试使雇员入场',
    121: '雇员入场时',
    122: '雇员入场成功',
    125: '尝试发动效果',
    126: '尝试支付代价',
    127: '支付代价后',
    128: '效果处理成功后',
    129: '效果处理失败后',
    130: '尝试放置策略',
    131: '放置策略后',
    132: '尝试放置雇员',
    133: '放置雇员',
    134: '回合开始时',
    135: '抽卡阶段开始时',
    136: '主要阶段1开始时',
    139: '回合结束时',
    141: '尝试发动攻击',
    142: '攻击宣言',
    143: '发生攻击时',
    144: '攻击伤害判定时',
    145: '攻击后',
    146: '被摧毁时',
    147: '被摧毁后',
    148: '离场时',
    149: '离场后',
    150: '离开手牌时',
    151: '离开手牌后',
    152: '离开主卡组时',
    153: '离开主卡组后',
    154: '离开副卡组时',
    155: '离开副卡组后',
    156: '离开场下时',
    157: '离开场下后',
    158: '离开移除区时',
    159: '离开移除区后',
    160: '入场时',
    161: '入场后',
    162: '加入手牌时',
    163: '加入手牌后',
    164: '加入主卡组时',
    165: '加入主卡组后',
    166: '加入副卡组时',
    167: '加入副卡组后',
    168: '进入场下时',
    169: '进入场下后',
    170: '加入移除区时',
    171: '加入移除区后',
    172: '尝试丢弃手牌',
    173: '丢弃手牌时',
    174: '被丢弃后',
    175: '尝试奉献',
    176: '奉献时',
    177: '奉献后',
    178: '尝试进行契约',
    179: '进行契约时',
    180: '进行契约后',
    181: '尝试抽卡',
    182: '抽卡时',
    183: '抽卡后',
    184: '使用筹码阶段将结束时',
    185: '尝试将效果无效',
    186: '效果将被无效时',
    187: '效果被无效后',
    188: '尝试阻挡',
    189: '阻挡时',
    190: '阻挡后',
    191: '展示卡时',
    192: '展示卡后',
}
