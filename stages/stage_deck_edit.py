from stages.stage_base import StageBase
from utils.color import color, color_print, EColor
from utils.common import list_cards, card_detail, random_deck,\
    rdk_add_card, rdk_remove_card, new_deck,\
    deck_add_card, deck_remove_card, remove_deck, open_deck,\
    pvp,\
    DEBUG
from utils.constants import ECardType, card_type,\
    employee_type, strategy_type, ECardRank

import json


class StageDeckEdit(StageBase):
    def __init__(self, st: list = None):
        super().__init__(st)

        self.deck_index = None
        self.rdk_editing = False
        self.rdk_a_time = 0
        self.rdk_rm_time = 0
        # 卡组修改操作栈，用于提交操作
        self.edit_stack = list()
        self.temp_deck = dict()
        self.side_editing = False

    def enter(self):
        color_print('\n----卡组编辑页面----')
        self.cmd_set['-l'] = (self.list_all_cards, '列出所有卡。')
        self.cmd_set['-ld'] = (self.list_all_cards, '列出所有已保存的卡组。')
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
                              '(rm 卡片名)移除当前卡组中 1 张指定'
                              '卡并显示修改后的卡组。')
        self.cmd_set['rmd'] = (self.remove_deck, '删除当前卡组。')
        self.cmd_set['-m'] = (self.edit_main_deck, '切换至主卡组编辑。')
        self.cmd_set['-s'] = (self.edit_side_deck, '切换至副卡组编辑。')
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

    def detail(self, *args):
        col = EColor.DEFAULT_COLOR
        card_name = ' '
        card_name = card_name.join(args)
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
        sts = list()
        if c['type'] == ECardType.EMPLOYEE.value:
            for st in employee_type.keys():
                if st & int(c['subtype']):
                    sts.append(employee_type[st])
            subtype = '|'.join(sts)
        elif c['type'] == ECardType.STRATEGY.value:
            for st in strategy_type.keys():
                if st & int(c['subtype']):
                    sts.append(strategy_type[st])
            subtype = '|'.join(sts)
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

    @staticmethod
    def __show_deck(deck: dict):
        color_print('主卡组: ', EColor.EMPHASIS)
        cl = [list(), list(), list(),
              list(), list(), list()]
        col = [EColor.TRUMP_CARD, EColor.GOOD_CARD, EColor.COMMON_CARD,
               EColor.TRUMP_CARD, EColor.GOOD_CARD, EColor.COMMON_CARD]
        for cid in deck.keys():
            rk = deck[cid][1]
            side = deck[cid][3]
            cl[ECardRank.TRUMP.value - rk + side * 3].append(cid)
        for i in range(0, 6):
            if i == 3:
                color_print('副卡组: ', EColor.EMPHASIS)
            for cid in cl[i]:
                color_print('{}: {}'.format(color(deck[cid][2], col[i]),
                                            deck[cid][0]))

    def __update_deck(self, deck: dict):
        """
        更新当前编辑的卡组并输出。
        :param deck:
        :return:
        """
        col = EColor.EMPHASIS
        self.temp_deck = dict()
        for cid in deck.keys():
            self.temp_deck[cid] = deck[cid]
        self.__show_deck(self.temp_deck)

    def random_deck(self):
        self.deck_index = None
        self.rdk_editing = True
        self.edit_stack = list()

        deck, self.rdk_a_time, self.rdk_rm_time = random_deck()
        self.__update_deck(deck)

    def new(self, deck_name):
        self.deck_index = int(new_deck(deck_name))
        self.rdk_editing = False
        self.edit_stack = list()
        self.temp_deck = dict()

    def remove_deck(self):
        try:
            remove_deck(self.deck_index)
        except Exception as ex:
            color_print('指定的卡组不存在orz', EColor.ERROR)

    def deck_open(self, deck_name):
        self.rdk_editing = False
        self.edit_stack = list()

        deck, self.deck_index = open_deck(deck_name)
        self.__update_deck(deck)

    def __add_card(self, card_name):
        c = card_detail(card_name)
        cid = str(c['card_id'])
        limit = c['limit']

        # 查找temp_deck重的对应项
        item = None
        if cid in self.temp_deck:
            item = self.temp_deck[cid]

        # 判断添加是否合法
        if item is None and limit > 0:
            self.temp_deck[cid] = [1, c['rank'], c['name'], self.side_editing]
            self.edit_stack.append((deck_add_card, c['card_id'], self.side_editing))
        elif limit > item[0]:
            self.temp_deck[cid][0] += 1
            self.edit_stack.append((deck_add_card, c['card_id'], self.side_editing))
        else:
            return False
        return True

    def add(self, *card_name):
        card_name = ' '.join(card_name)
        if self.deck_index is not None:
            f = self.__add_card(card_name)
            self.__show_deck(self.temp_deck)
            return f
        elif self.rdk_editing:
            if self.rdk_a_time < 2:
                self.rdk_a_time += 1
                f = self.__add_card(card_name)
                self.__show_deck(self.temp_deck)
                return f
            color_print('至多可以对随机卡组修改2次orz', EColor.ERROR)
        else:
            color_print('当前没有在编辑任何卡组orz', EColor.ERROR)
        return False

    def fill(self, *card_name):
        card_name = ' '.join(card_name)
        if self.deck_index is not None:
            while self.__add_card(card_name):
                pass
            self.__show_deck(self.temp_deck)
        elif self.rdk_editing:
            f = False
            while self.__add_card(card_name):
                f = True
                if self.rdk_a_time <= 2:
                    self.rdk_a_time += 1
                pass
            self.__show_deck(self.temp_deck)
            if not f:
                color_print('至多可以对随机卡组修改2次orz', EColor.ERROR)
        else:
            color_print('当前没有在编辑任何卡组orz', EColor.ERROR)

    def __remove(self, card_name):
        c = card_detail(card_name)
        cid = str(c['card_id'])
        if cid in self.temp_deck:
            self.edit_stack.append((deck_remove_card, c['card_id'], self.side_editing))
            if self.temp_deck[cid][0] > 1:
                self.temp_deck[cid][0] -= 1
            else:
                self.temp_deck.pop(cid)
            self.__show_deck(self.temp_deck)
        else:
            color_print('{}不存在于当前卡组orz'.format(card_name), EColor.ERROR)

    def remove(self, *card_name):
        card_name = ' '.join(card_name)
        if self.deck_index is not None:
            self.__remove(card_name)
        elif self.rdk_editing:
            if self.rdk_rm_time < 2:
                self.rdk_rm_time += 1
            else:
                color_print('至多可以对随机卡组修改2次orz', EColor.ERROR)
                return
            self.__remove(card_name)
        else:
            color_print('当前没有在编辑任何卡组orz', EColor.ERROR)

    def edit_main_deck(self):
        self.side_editing = False

    def edit_side_deck(self):
        self.side_editing = True

    def save(self):
        d = None
        if self.deck_index is not None:
            for e in self.edit_stack:
                d = e[0](e[1], self.deck_index, e[2])
        elif self.rdk_editing:
            for e in self.edit_stack:
                d = e[0](e[1], None, 0)
        else:
            color_print('当前没有在编辑任何卡组orz', EColor.ERROR)
            return
        self.edit_stack = list()
        if d is not None:
            self.__update_deck(d)
        else:
            self.__show_deck(self.temp_deck)

    def play(self):
        from stages.stage_pvp import StagePVP
        if pvp(self.deck_index, -1):
            self.next_stage = StagePVP(self.status)
        else:
            color_print('匹配失败orz', EColor.ERROR)

    def play_with_secret_code(self, code):
        pass
