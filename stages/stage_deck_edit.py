from stages.stage_base import StageBase
from utils.color import color, color_print, EColor
from utils.common import list_cards, card_detail, random_deck, DEBUG
from utils.constants import ECardType, card_type,\
    employee_type, strategy_type, ECardRank
import json


class StageDeckEdit(StageBase):
    def enter(self):
        color_print('\n----卡组编辑页面----')
        self.cmd_set['-l'] = (self.list_all_cards, '列出所有卡。')
        self.cmd_set['-d'] = (self.detail, '(-d 卡片名)显示指定卡的详细信息。')

        self.cmd_set['rdk'] = (self.random_deck, '获得今日的随机卡组并开始编辑。(每天至多获取 1 个)')
        self.cmd_set['new'] = (self.new,
                               '(new 新卡组名)添加新的卡组并开始编辑。')
        self.cmd_set['op'] = (self.deck_open,
                              '(op 已有卡组名)打开指定卡组并开始编辑。')
        self.cmd_set['a'] = (self.add,
                               '(a 卡片名)添加 1 张指定的卡到当前'
                               '卡组并显示修改后的卡组。')
        self.cmd_set['fi'] = (self.fill,
                              '(fi 卡片名)尽可能地添加指定地卡到当前'
                              '卡组并显示修改后的卡组。')
        self.cmd_set['rm'] = (self.remove,
                              '(rm 卡片序号)移除当前卡组中 1 张指定'
                              '序号的卡并显示修改后的卡组。')
        self.cmd_set['s'] = (self.save, '保存对当前卡组的修改。')
        self.cmd_set['p'] = (self.play, '使用当前卡组与随机对手进行一场\"公平交易\"！(3局2胜)')
        self.cmd_set['pwd'] = (self.play_with_secret_code, '(pwd 4位数字)使用暗号进行一场私下的\"公平交易\"……(3局2胜)')
        super().enter()

    def list_all_cards(self):
        j = list_cards()
        col = EColor.DEFAULT_COLOR
        for c in j:
            if c['rank'] == ECardRank.COMMON.value:
                col = EColor.COMMON_CARD
            elif c['rank'] == ECardRank.GOOD.value:
                col = EColor.GOOD_CARD
            elif c['rank'] == ECardRank.TRUMP.value:
                col = EColor.TRUMP_CARD
            color_print('{}({})'.format(color(c['name'], col), c['limit']))

    def detail(self, card_name):
        col = EColor.DEFAULT_COLOR
        c = card_detail(card_name)
        if c['rank'] == ECardRank.COMMON.value:
            col = EColor.COMMON_CARD
        elif c['rank'] == ECardRank.GOOD.value:
            col = EColor.GOOD_CARD
        elif c['rank'] == ECardRank.TRUMP.value:
            col = EColor.TRUMP_CARD
        if DEBUG:
            color_print('{} {}'.format(color(c['name'], col), c['card_id']))
        else:
            color_print('{}'.format(color(c['name'], col)))
        subtype = ''
        if c['type'] == ECardType.EMPLOYEE.value:
            subtype = employee_type[int(c['subtype'])]
        elif c['type'] == ECardType.STRATEGY.value:
            subtype = strategy_type[int(c['subtype'])]
        color_print('{} {}'.format(card_type[int(c['type'])], subtype))
        ss = ''
        if len(c['series']) > 0:
            ss = str(c['series'])
        if c['type'] == ECardType.EMPLOYEE.value:
            color_print('ATK {} DEF {} {}'.format(color(c['atk_eff'], EColor.ATK),
                                               color(c['def_hp'], EColor.DEF), ss))
        elif c['type'] == ECardType.STRATEGY.value:
            color_print('EFF {} {}'.format(color(c['atk_eff'], EColor.DEF), ss))
        color_print('效果: {}'.format(c['effect']))

    def random_deck(self):
        deck = None
        try:
            deck = random_deck()
        except Exception as ex:
            color_print('您今日已经获取过1次随机卡组了orz', EColor.ERROR)
            return
        col = EColor.EMPHASIS
        for cn in deck.keys():
            rk = deck[cn][1]
            if rk == ECardRank.COMMON.value:
                col = EColor.COMMON_CARD
            elif rk == ECardRank.GOOD.value:
                col = EColor.GOOD_CARD
            elif rk == ECardRank.TRUMP.value:
                col = EColor.TRUMP_CARD
            color_print('{}: {}'.format(color(cn, col),
                                        deck[cn][0]))


    def new(self, deck_name):
        pass

    def deck_open(self, deck_name):
        pass

    def add(self, card_name):
        pass

    def fill(self, card_name):
        pass

    def remove(self, index):
        pass

    def save(self):
        pass

    def play(self):
        pass

    def play_with_secret_code(self, code):
        pass
